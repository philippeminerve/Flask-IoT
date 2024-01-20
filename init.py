from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import distinct
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import plotly.express as px

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Modèle de données
class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    data_type = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Fonction pour initialiser la base de données
def init_db():
    with app.app_context():
        db.create_all()

# Endpoint pour sauvegarder des données
@app.route('/save_data')
def save_data():
    user_id = request.args.get('id')
    data_type = request.args.get('data')
    value = request.args.get('value')

    if user_id and data_type and value:
        new_data_point = DataPoint(user_id=user_id, data_type=data_type, value=value)
        db.session.add(new_data_point)
        db.session.commit()
        return 'Données enregistrées avec succès.'
    else:
        return 'Paramètres manquants.'

# Endpoint pour le tableau de bord avec graphique interactif
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Obtenir la liste des utilisateurs distincts
    users = [user[0] for user in db.session.query(distinct(DataPoint.user_id)).all()]

    # Obtenir la liste des types de données distincts
    data_types = [data_type[0] for data_type in db.session.query(distinct(DataPoint.data_type)).all()]

    if request.method == 'POST':
        selected_user = request.form.get('selected_user')
        selected_data_type = request.form.get('selected_data_type')

        # Sélectionner les données spécifiques à l'utilisateur et au type de données
        data_points = DataPoint.query.filter_by(user_id=selected_user, data_type=selected_data_type).all()

        # Convertir les objets timestamp en chaînes de caractères
        data_points = [{'timestamp': str(point.timestamp), 'value': point.value} for point in data_points]

        # Créer le graphique Plotly
        fig = px.line(data_points, x='timestamp', y='value', title=f'Graphique pour {selected_data_type} - Utilisateur {selected_user}')

        # Afficher le graphique en utilisant le format HTML
        graph_html = fig.to_html(full_html=False)

        return render_template('dashboard.html', users=users, data_types=data_types, graph_html=graph_html, selected_user=selected_user, selected_data_type=selected_data_type)

    return render_template('dashboard.html', users=users, data_types=data_types)


if __name__ == '__main__':
    init_db()
    app.run(debug=True,host='0.0.0.0',port=5000)
