from datetime import datetime
from functools import wraps
import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pfe-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///pfe.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

module_professeur_tp = db.Table(
    'module_professeur_tp',
    db.Column('module_id', db.Integer, db.ForeignKey('module.id'), primary_key=True),
    db.Column('professeur_id', db.Integer, db.ForeignKey('professeur.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, professeur
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeur.id'), nullable=True)

    professeur = db.relationship('Professeur', backref='user_account', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Filiere(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)


class Annee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(50), nullable=False)


class Semestre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(10), nullable=False)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    annee_id = db.Column(db.Integer, db.ForeignKey('annee.id'), nullable=False)
    annee = db.relationship('Annee', backref='semestres')


class Groupe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    filiere_id = db.Column(db.Integer, db.ForeignKey('filiere.id'), nullable=False)
    annee_id = db.Column(db.Integer, db.ForeignKey('annee.id'), nullable=False)

    filiere = db.relationship('Filiere', backref='groupes')
    annee = db.relationship('Annee', backref='groupes')


class Professeur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    specialite = db.Column(db.String(120))


class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_apogee = db.Column(db.String(50), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email_academique = db.Column(db.String(150), unique=True, nullable=False)
    photo = db.Column(db.String(255), default='https://via.placeholder.com/60x60.png?text=Photo')
    statut = db.Column(db.String(20), default='actif')  # actif, abandonne
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupe.id'), nullable=False)

    groupe = db.relationship('Groupe', backref='etudiants')


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    nom = db.Column(db.String(150), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)
    filiere_id = db.Column(db.Integer, db.ForeignKey('filiere.id'), nullable=False)
    heures_cours = db.Column(db.Integer, default=0)
    heures_tp = db.Column(db.Integer, default=0)
    semaine_debut_cours = db.Column(db.Integer)
    semaine_fin_cours = db.Column(db.Integer)
    semaine_debut_tp = db.Column(db.Integer)
    semaine_fin_tp = db.Column(db.Integer)
    professeur_cours_id = db.Column(db.Integer, db.ForeignKey('professeur.id'))

    semestre = db.relationship('Semestre', backref='modules')
    filiere = db.relationship('Filiere', backref='modules')
    professeur_cours = db.relationship('Professeur', foreign_keys=[professeur_cours_id], backref='modules_cours')
    professeurs_tp = db.relationship('Professeur', secondary=module_professeur_tp, backref='modules_tp')


class Seance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupe.id'), nullable=False)
    type_seance = db.Column(db.String(20), nullable=False)  # cours, tp, examen
    jour = db.Column(db.String(20), nullable=False)
    creneau = db.Column(db.Integer, nullable=False)
    semaine = db.Column(db.Integer, nullable=False)
    date_seance = db.Column(db.Date, nullable=False)
    duree_heures = db.Column(db.Integer, default=4)

    module = db.relationship('Module', backref='seances')
    groupe = db.relationship('Groupe', backref='seances')


class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    seance_id = db.Column(db.Integer, db.ForeignKey('seance.id'), nullable=False)
    justifiee = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant = db.relationship('Etudiant', backref='absences')
    seance = db.relationship('Seance', backref='absences')

    __table_args__ = (db.UniqueConstraint('etudiant_id', 'seance_id', name='uq_absence_etudiant_seance'),)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)
    type_note = db.Column(db.String(20), nullable=False)  # controle, examen
    valeur = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant = db.relationship('Etudiant', backref='notes')
    module = db.relationship('Module', backref='notes')
    semestre = db.relationship('Semestre', backref='notes')


class Avertissement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    niveau = db.Column(db.String(50), nullable=False)
    motif = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant = db.relationship('Etudiant', backref='avertissements')


DAYS = {
    'Lundi': 4,
    'Mardi': 4,
    'Mercredi': 4,
    'Jeudi': 4,
    'Vendredi': 4,
    'Samedi': 2,
}


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Veuillez vous connecter.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Accès non autorisé.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def current_user():
    uid = session.get('user_id')
    return db.session.get(User, uid) if uid else None


def generate_warning_for_student(etudiant_id):
    absences_count = db.session.query(Absence).join(Etudiant).filter(Etudiant.id == etudiant_id).count()
    levels = {1: 'Premier avertissement', 2: 'Deuxième avertissement'}
    if absences_count in levels:
        exists = Avertissement.query.filter_by(etudiant_id=etudiant_id, niveau=levels[absences_count]).first()
        if not exists:
            db.session.add(Avertissement(
                etudiant_id=etudiant_id,
                niveau=levels[absences_count],
                motif=f'{absences_count} absence(s) enregistrée(s)'
            ))
    elif absences_count >= 3:
        exists = Avertissement.query.filter_by(etudiant_id=etudiant_id, niveau='Conseil de discipline').first()
        if not exists:
            db.session.add(Avertissement(
                etudiant_id=etudiant_id,
                niveau='Conseil de discipline',
                motif='Absences répétées'
            ))


def update_abandon_status(etudiant_id):
    exam_absence = db.session.query(Absence).join(Seance).filter(
        Absence.etudiant_id == etudiant_id,
        Seance.type_seance == 'examen'
    ).count() > 0

    notes_count = Note.query.filter_by(etudiant_id=etudiant_id).count()

    etudiant = db.session.get(Etudiant, etudiant_id)
    if etudiant and exam_absence and notes_count == 0:
        etudiant.statut = 'abandonne'


@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('prof_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Connexion réussie.', 'success')
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'prof_dashboard'))
        flash('Identifiants invalides.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion effectuée.', 'info')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    total_students = Etudiant.query.filter_by(statut='actif').count()
    total_profs = Professeur.query.count()
    total_modules = Module.query.count()
    abandoned = Etudiant.query.filter_by(statut='abandonne').count()
    total_absences = db.session.query(Absence).join(Etudiant).filter(Etudiant.statut == 'actif').count()

    absence_by_module = db.session.query(Module.nom, func.count(Absence.id)).join(Seance, Seance.module_id == Module.id).join(
        Absence, Absence.seance_id == Seance.id, isouter=True
    ).group_by(Module.nom).all()

    avg_notes = db.session.query(Module.nom, func.avg(Note.valeur)).join(Note, Note.module_id == Module.id, isouter=True).group_by(Module.nom).all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_profs=total_profs,
        total_modules=total_modules,
        abandoned=abandoned,
        total_absences=total_absences,
        absence_by_module=absence_by_module,
        avg_notes=avg_notes,
    )


@app.route('/admin/etudiants', methods=['GET', 'POST'])
@login_required('admin')
def students_management():
    if request.method == 'POST':
        e = Etudiant(
            code_apogee=request.form['code_apogee'],
            nom=request.form['nom'],
            prenom=request.form['prenom'],
            email_academique=request.form['email_academique'],
            photo=request.form.get('photo') or 'https://via.placeholder.com/60x60.png?text=Photo',
            groupe_id=int(request.form['groupe_id'])
        )
        db.session.add(e)
        db.session.commit()
        flash('Étudiant ajouté.', 'success')
        return redirect(url_for('students_management'))

    etudiants = Etudiant.query.order_by(Etudiant.nom).all()
    groupes = Groupe.query.order_by(Groupe.nom).all()
    return render_template('students.html', etudiants=etudiants, groupes=groupes)


@app.route('/admin/modules', methods=['GET', 'POST'])
@login_required('admin')
def modules_management():
    if request.method == 'POST':
        m = Module(
            code=request.form['code'],
            nom=request.form['nom'],
            semestre_id=int(request.form['semestre_id']),
            filiere_id=int(request.form['filiere_id']),
            heures_cours=int(request.form.get('heures_cours') or 0),
            heures_tp=int(request.form.get('heures_tp') or 0),
            semaine_debut_cours=int(request.form.get('semaine_debut_cours') or 1),
            semaine_fin_cours=int(request.form.get('semaine_fin_cours') or 1),
            semaine_debut_tp=int(request.form.get('semaine_debut_tp') or 1),
            semaine_fin_tp=int(request.form.get('semaine_fin_tp') or 1),
            professeur_cours_id=int(request.form['professeur_cours_id']) if request.form.get('professeur_cours_id') else None
        )
        db.session.add(m)
        db.session.commit()
        flash('Module ajouté.', 'success')
        return redirect(url_for('modules_management'))

    modules = Module.query.order_by(Module.nom).all()
    semestres = Semestre.query.all()
    filieres = Filiere.query.all()
    professeurs = Professeur.query.order_by(Professeur.nom).all()
    return render_template('modules.html', modules=modules, semestres=semestres, filieres=filieres, professeurs=professeurs)


@app.route('/admin/groupes', methods=['GET', 'POST'])
@login_required('admin')
def groups_management():
    if request.method == 'POST':
        g = Groupe(
            nom=request.form['nom'],
            filiere_id=int(request.form['filiere_id']),
            annee_id=int(request.form['annee_id'])
        )
        db.session.add(g)
        db.session.commit()
        flash('Groupe ajouté.', 'success')
        return redirect(url_for('groups_management'))

    groupes = Groupe.query.order_by(Groupe.nom).all()
    filieres = Filiere.query.all()
    annees = Annee.query.all()
    return render_template('groups.html', groupes=groupes, filieres=filieres, annees=annees)


@app.route('/admin/statistiques')
@login_required('admin')
def statistiques():
    active_students = Etudiant.query.filter_by(statut='actif').count()
    total_absences = db.session.query(Absence).join(Etudiant).filter(Etudiant.statut == 'actif').count()
    taux_global = round((total_absences / active_students), 2) if active_students else 0

    absence_by_group = db.session.query(Groupe.nom, func.count(Absence.id)).join(Etudiant, Etudiant.groupe_id == Groupe.id).join(
        Absence, Absence.etudiant_id == Etudiant.id, isouter=True
    ).filter(Etudiant.statut == 'actif').group_by(Groupe.nom).all()

    corr_data = db.session.query(
        Etudiant.nom,
        func.count(Absence.id).label('absences'),
        func.avg(Note.valeur).label('moyenne')
    ).outerjoin(Absence, Absence.etudiant_id == Etudiant.id).outerjoin(Note, Note.etudiant_id == Etudiant.id).filter(
        Etudiant.statut == 'actif'
    ).group_by(Etudiant.id, Etudiant.nom).all()

    return render_template('statistics.html', taux_global=taux_global, absence_by_group=absence_by_group, corr_data=corr_data)


@app.route('/admin/abandons')
@login_required('admin')
def abandoned_students():
    etudiants = Etudiant.query.filter_by(statut='abandonne').all()
    return render_template('abandoned_students.html', etudiants=etudiants)


@app.route('/prof/dashboard')
@login_required('professeur')
def prof_dashboard():
    user = current_user()
    professeur = user.professeur
    modules = []
    if professeur:
        modules = list({m.id: m for m in (professeur.modules_cours + professeur.modules_tp)}.values())
    return render_template('prof_dashboard.html', professeur=professeur, modules=modules)


@app.route('/prof/absences', methods=['GET', 'POST'])
@login_required('professeur')
def absence_entry():
    user = current_user()
    professeur = user.professeur
    modules = list({m.id: m for m in (professeur.modules_cours + professeur.modules_tp)}) if professeur else []
    selected_module_id = request.args.get('module_id', type=int) or request.form.get('module_id', type=int)
    selected_group_id = request.args.get('groupe_id', type=int) or request.form.get('groupe_id', type=int)
    seance_id = request.args.get('seance_id', type=int) or request.form.get('seance_id', type=int)

    groupes = []
    seances = []
    etudiants = []
    checked_ids = set()

    if selected_module_id:
        groupes = Groupe.query.join(Seance).filter(Seance.module_id == selected_module_id).distinct().all()
        if selected_group_id:
            seances = Seance.query.filter_by(module_id=selected_module_id, groupe_id=selected_group_id).order_by(Seance.date_seance.desc()).all()
            etudiants = Etudiant.query.filter_by(groupe_id=selected_group_id, statut='actif').order_by(Etudiant.nom).all()
        if seance_id:
            checked_ids = {a.etudiant_id for a in Absence.query.filter_by(seance_id=seance_id).all()}

    if request.method == 'POST' and seance_id:
        current_absences = Absence.query.filter_by(seance_id=seance_id).all()
        current_ids = {a.etudiant_id for a in current_absences}
        selected_ids = {int(x) for x in request.form.getlist('absents')}

        for absence in current_absences:
            if absence.etudiant_id not in selected_ids:
                db.session.delete(absence)

        for student_id in selected_ids - current_ids:
            db.session.add(Absence(etudiant_id=student_id, seance_id=seance_id))
            generate_warning_for_student(student_id)
            update_abandon_status(student_id)

        db.session.commit()
        flash('Absences enregistrées.', 'success')
        return redirect(url_for('absence_entry', module_id=selected_module_id, groupe_id=selected_group_id, seance_id=seance_id))

    return render_template(
        'absence_entry.html',
        modules=modules,
        groupes=groupes,
        seances=seances,
        etudiants=etudiants,
        selected_module_id=selected_module_id,
        selected_group_id=selected_group_id,
        seance_id=seance_id,
        checked_ids=checked_ids,
    )


@app.route('/prof/notes', methods=['GET', 'POST'])
@login_required('professeur')
def note_entry():
    user = current_user()
    professeur = user.professeur
    modules = list({m.id: m for m in (professeur.modules_cours + professeur.modules_tp)}) if professeur else []
    selected_module_id = request.args.get('module_id', type=int) or request.form.get('module_id', type=int)
    selected_group_id = request.args.get('groupe_id', type=int) or request.form.get('groupe_id', type=int)

    groupes = []
    etudiants = []
    module = None

    if selected_module_id:
        module = db.session.get(Module, selected_module_id)
        groupes = Groupe.query.join(Seance).filter(Seance.module_id == selected_module_id).distinct().all()
        if selected_group_id:
            etudiants = Etudiant.query.filter_by(groupe_id=selected_group_id, statut='actif').order_by(Etudiant.nom).all()

    if request.method == 'POST' and module:
        for etudiant in Etudiant.query.filter_by(groupe_id=selected_group_id, statut='actif').all():
            controle = request.form.get(f'controle_{etudiant.id}')
            examen = request.form.get(f'examen_{etudiant.id}')
            for type_note, val in [('controle', controle), ('examen', examen)]:
                if val not in (None, ''):
                    existing = Note.query.filter_by(etudiant_id=etudiant.id, module_id=module.id, semestre_id=module.semestre_id, type_note=type_note).first()
                    if existing:
                        existing.valeur = float(val)
                    else:
                        db.session.add(Note(
                            etudiant_id=etudiant.id,
                            module_id=module.id,
                            semestre_id=module.semestre_id,
                            type_note=type_note,
                            valeur=float(val)
                        ))
        db.session.commit()
        flash('Notes enregistrées.', 'success')
        return redirect(url_for('note_entry', module_id=selected_module_id, groupe_id=selected_group_id))

    notes_map = {}
    if module and selected_group_id:
        notes = Note.query.join(Etudiant).filter(Note.module_id == module.id, Etudiant.groupe_id == selected_group_id).all()
        notes_map = {(n.etudiant_id, n.type_note): n.valeur for n in notes}

    return render_template(
        'note_entry.html',
        modules=modules,
        groupes=groupes,
        etudiants=etudiants,
        selected_module_id=selected_module_id,
        selected_group_id=selected_group_id,
        notes_map=notes_map
    )


@app.route('/prof/historique/<int:etudiant_id>')
@login_required('professeur')
def student_history(etudiant_id):
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    absences = Absence.query.join(Seance).filter(Absence.etudiant_id == etudiant_id).order_by(Seance.date_seance.desc()).all()
    notes = Note.query.filter_by(etudiant_id=etudiant_id).order_by(Note.created_at.desc()).all()
    avertissements = Avertissement.query.filter_by(etudiant_id=etudiant_id).order_by(Avertissement.created_at.desc()).all()
    return render_template('student_history.html', etudiant=etudiant, absences=absences, notes=notes, avertissements=avertissements)


@app.route('/seed')
def seed_data():
    if User.query.first():
        return 'Base déjà initialisée.'

    a1 = Annee(libelle='1ère année')
    a2 = Annee(libelle='2ème année')
    f1 = Filiere(nom='Informatique Décisionnelle', description='DUT EST Fès')
    s1 = Semestre(libelle='S1', annee=a1)
    s2 = Semestre(libelle='S2', annee=a1)
    g1 = Groupe(nom='ID-1A-G1', filiere=f1, annee=a1)
    g2 = Groupe(nom='ID-1A-G2', filiere=f1, annee=a1)
    p1 = Professeur(nom='El Amrani', prenom='Sara', email='sara.prof@estf.ma', specialite='BI')
    p2 = Professeur(nom='Alaoui', prenom='Youssef', email='youssef.prof@estf.ma', specialite='Base de données')
    m1 = Module(code='BD101', nom='Bases de données', semestre=s1, filiere=f1, heures_cours=24, heures_tp=16,
                semaine_debut_cours=1, semaine_fin_cours=6, semaine_debut_tp=2, semaine_fin_tp=5, professeur_cours=p2)
    m2 = Module(code='BI102', nom='Business Intelligence', semestre=s1, filiere=f1, heures_cours=20, heures_tp=20,
                semaine_debut_cours=1, semaine_fin_cours=5, semaine_debut_tp=3, semaine_fin_tp=7, professeur_cours=p1)
    m1.professeurs_tp.append(p1)
    e1 = Etudiant(code_apogee='AP001', nom='Bennani', prenom='Imane', email_academique='imane.bennani@estf.ma', groupe=g1)
    e2 = Etudiant(code_apogee='AP002', nom='Lahlou', prenom='Adam', email_academique='adam.lahlou@estf.ma', groupe=g1)
    e3 = Etudiant(code_apogee='AP003', nom='Tahiri', prenom='Salma', email_academique='salma.tahiri@estf.ma', groupe=g2)
    admin = User(username='admin', role='admin')
    admin.set_password('admin123')
    u1 = User(username='sara.prof', role='professeur', professeur=p1)
    u1.set_password('prof123')
    u2 = User(username='youssef.prof', role='professeur', professeur=p2)
    u2.set_password('prof123')

    db.session.add_all([a1, a2, f1, s1, s2, g1, g2, p1, p2, m1, m2, e1, e2, e3, admin, u1, u2])
    db.session.flush()

    seances = [
        Seance(module=m1, groupe=g1, type_seance='cours', jour='Lundi', creneau=1, semaine=1, date_seance=datetime(2026, 2, 2).date()),
        Seance(module=m1, groupe=g1, type_seance='tp', jour='Mercredi', creneau=2, semaine=2, date_seance=datetime(2026, 2, 11).date()),
        Seance(module=m2, groupe=g1, type_seance='cours', jour='Mardi', creneau=3, semaine=1, date_seance=datetime(2026, 2, 3).date()),
        Seance(module=m2, groupe=g1, type_seance='examen', jour='Jeudi', creneau=1, semaine=10, date_seance=datetime(2026, 4, 16).date()),
        Seance(module=m1, groupe=g2, type_seance='cours', jour='Lundi', creneau=2, semaine=1, date_seance=datetime(2026, 2, 2).date()),
    ]
    db.session.add_all(seances)
    db.session.commit()
    return 'Données de démonstration créées. Admin: admin/admin123 ; Prof: sara.prof/prof123'


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow(), 'days': DAYS}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
