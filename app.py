import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Get the absolute path for database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'akesis.db'

app.config['SECRET_KEY'] = 'change-this-to-a-random-secret-key-for-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODELS ====================

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="Where Color Speaks, Art Heals")
    subtitle = db.Column(db.String(300), nullable=False, default="Handcrafted crochet fashion, wearable art, and mixed media pieces that celebrate emotion, color, and individuality.")
    button1_text = db.Column(db.String(50), nullable=False, default="Shop Now")
    button2_text = db.Column(db.String(50), nullable=False, default="Our Story")

class UniqueFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default="Meet the Maker")
    content = db.Column(db.Text, nullable=False)
    maker_name = db.Column(db.String(100), nullable=False, default="Samuella Bennie Coffie")
    maker_title = db.Column(db.String(200), nullable=False, default="multidisciplinary artist, chromotherapist, and lifelong lover of color")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    gradient_from = db.Column(db.String(50), nullable=False, default="purple-400")
    gradient_to = db.Column(db.String(50), nullable=False, default="pink-500")
    order = db.Column(db.Integer, default=0)

class JourneyMilestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    color = db.Column(db.String(50), nullable=False, default="purple-700")
    order = db.Column(db.Integer, default=0)

class WhyChooseUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0)

class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, default="akesiskreation@gmail.com")
    phone = db.Column(db.String(50), nullable=False, default="+233 26 505 2819")
    shipping_info = db.Column(db.String(200), nullable=False, default="We ship worldwide via DHL")
    instagram = db.Column(db.String(200), nullable=False, default="#")
    tiktok = db.Column(db.String(200), nullable=False, default="#")
    facebook = db.Column(db.String(200), nullable=False, default="#")
    pinterest = db.Column(db.String(200), nullable=False, default="#")

class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False, default="Akesi's Kreation")
    tagline = db.Column(db.String(200), nullable=False, default="Where Color Speaks, Art Heals")
    footer_text = db.Column(db.String(200), nullable=False, default="Where Color Speaks, Art Heals")

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

# ==================== AUTH DECORATOR ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    hero = HeroSection.query.first()
    features = UniqueFeature.query.order_by(UniqueFeature.order).all()
    about = AboutSection.query.first()
    products = Product.query.order_by(Product.order).all()
    milestones = JourneyMilestone.query.order_by(JourneyMilestone.order).all()
    why_choose = WhyChooseUs.query.order_by(WhyChooseUs.order).all()
    contact_info = ContactInfo.query.first()
    settings = SiteSetting.query.first()
    
    return render_template('index.html', 
                         hero=hero, 
                         features=features, 
                         about=about,
                         products=products,
                         milestones=milestones,
                         why_choose=why_choose,
                         contact_info=contact_info,
                         settings=settings)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    return render_template('admin/dashboard.html', messages=messages, unread_count=unread_count)

# Hero Section Management
@app.route('/admin/hero', methods=['GET', 'POST'])
@login_required
def admin_hero():
    hero = HeroSection.query.first()
    if not hero:
        hero = HeroSection()
        db.session.add(hero)
        db.session.commit()
    
    if request.method == 'POST':
        hero.title = request.form['title']
        hero.subtitle = request.form['subtitle']
        hero.button1_text = request.form['button1_text']
        hero.button2_text = request.form['button2_text']
        db.session.commit()
        flash('Hero section updated successfully!', 'success')
        return redirect(url_for('admin_hero'))
    
    return render_template('admin/hero.html', hero=hero)

# Features Management
@app.route('/admin/features')
@login_required
def admin_features():
    features = UniqueFeature.query.order_by(UniqueFeature.order).all()
    return render_template('admin/features.html', features=features)

@app.route('/admin/features/add', methods=['GET', 'POST'])
@login_required
def admin_feature_add():
    if request.method == 'POST':
        feature = UniqueFeature(
            icon=request.form['icon'],
            title=request.form['title'],
            description=request.form['description'],
            order=int(request.form.get('order', 0))
        )
        db.session.add(feature)
        db.session.commit()
        flash('Feature added successfully!', 'success')
        return redirect(url_for('admin_features'))
    return render_template('admin/feature_form.html', feature=None)

@app.route('/admin/features/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_feature_edit(id):
    feature = UniqueFeature.query.get_or_404(id)
    if request.method == 'POST':
        feature.icon = request.form['icon']
        feature.title = request.form['title']
        feature.description = request.form['description']
        feature.order = int(request.form.get('order', 0))
        db.session.commit()
        flash('Feature updated successfully!', 'success')
        return redirect(url_for('admin_features'))
    return render_template('admin/feature_form.html', feature=feature)

@app.route('/admin/features/delete/<int:id>')
@login_required
def admin_feature_delete(id):
    feature = UniqueFeature.query.get_or_404(id)
    db.session.delete(feature)
    db.session.commit()
    flash('Feature deleted successfully!', 'success')
    return redirect(url_for('admin_features'))

# Products Management
@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.order_by(Product.order).all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_product_add():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            icon=request.form['icon'],
            gradient_from=request.form['gradient_from'],
            gradient_to=request.form['gradient_to'],
            order=int(request.form.get('order', 0))
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None)

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_product_edit(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.icon = request.form['icon']
        product.gradient_from = request.form['gradient_from']
        product.gradient_to = request.form['gradient_to']
        product.order = int(request.form.get('order', 0))
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=product)

@app.route('/admin/products/delete/<int:id>')
@login_required
def admin_product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

# About Section Management
@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    about = AboutSection.query.first()
    if not about:
        about = AboutSection()
        db.session.add(about)
        db.session.commit()
    
    if request.method == 'POST':
        about.title = request.form['title']
        about.content = request.form['content']
        about.maker_name = request.form['maker_name']
        about.maker_title = request.form['maker_title']
        db.session.commit()
        flash('About section updated successfully!', 'success')
        return redirect(url_for('admin_about'))
    
    return render_template('admin/about.html', about=about)

# Journey Milestones Management
@app.route('/admin/milestones')
@login_required
def admin_milestones():
    milestones = JourneyMilestone.query.order_by(JourneyMilestone.order).all()
    return render_template('admin/milestones.html', milestones=milestones)

@app.route('/admin/milestones/add', methods=['GET', 'POST'])
@login_required
def admin_milestone_add():
    if request.method == 'POST':
        milestone = JourneyMilestone(
            year=request.form['year'],
            title=request.form['title'],
            description=request.form['description'],
            color=request.form['color'],
            order=int(request.form.get('order', 0))
        )
        db.session.add(milestone)
        db.session.commit()
        flash('Milestone added successfully!', 'success')
        return redirect(url_for('admin_milestones'))
    return render_template('admin/milestone_form.html', milestone=None)

@app.route('/admin/milestones/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_milestone_edit(id):
    milestone = JourneyMilestone.query.get_or_404(id)
    if request.method == 'POST':
        milestone.year = request.form['year']
        milestone.title = request.form['title']
        milestone.description = request.form['description']
        milestone.color = request.form['color']
        milestone.order = int(request.form.get('order', 0))
        db.session.commit()
        flash('Milestone updated successfully!', 'success')
        return redirect(url_for('admin_milestones'))
    return render_template('admin/milestone_form.html', milestone=milestone)

@app.route('/admin/milestones/delete/<int:id>')
@login_required
def admin_milestone_delete(id):
    milestone = JourneyMilestone.query.get_or_404(id)
    db.session.delete(milestone)
    db.session.commit()
    flash('Milestone deleted successfully!', 'success')
    return redirect(url_for('admin_milestones'))

# Why Choose Us Management
@app.route('/admin/whychoose')
@login_required
def admin_whychoose():
    items = WhyChooseUs.query.order_by(WhyChooseUs.order).all()
    return render_template('admin/whychoose.html', items=items)

@app.route('/admin/whychoose/add', methods=['GET', 'POST'])
@login_required
def admin_whychoose_add():
    if request.method == 'POST':
        item = WhyChooseUs(
            icon=request.form['icon'],
            title=request.form['title'],
            description=request.form['description'],
            order=int(request.form.get('order', 0))
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('admin_whychoose'))
    return render_template('admin/whychoose_form.html', item=None)

@app.route('/admin/whychoose/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_whychoose_edit(id):
    item = WhyChooseUs.query.get_or_404(id)
    if request.method == 'POST':
        item.icon = request.form['icon']
        item.title = request.form['title']
        item.description = request.form['description']
        item.order = int(request.form.get('order', 0))
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('admin_whychoose'))
    return render_template('admin/whychoose_form.html', item=item)

@app.route('/admin/whychoose/delete/<int:id>')
@login_required
def admin_whychoose_delete(id):
    item = WhyChooseUs.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('admin_whychoose'))

# Contact Info Management
@app.route('/admin/contact-info', methods=['GET', 'POST'])
@login_required
def admin_contact_info():
    contact = ContactInfo.query.first()
    if not contact:
        contact = ContactInfo()
        db.session.add(contact)
        db.session.commit()
    
    if request.method == 'POST':
        contact.email = request.form['email']
        contact.phone = request.form['phone']
        contact.shipping_info = request.form['shipping_info']
        contact.instagram = request.form['instagram']
        contact.tiktok = request.form['tiktok']
        contact.facebook = request.form['facebook']
        contact.pinterest = request.form['pinterest']
        db.session.commit()
        flash('Contact information updated successfully!', 'success')
        return redirect(url_for('admin_contact_info'))
    
    return render_template('admin/contact_info.html', contact=contact)

# Site Settings
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = SiteSetting.query.first()
    if not settings:
        settings = SiteSetting()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.site_name = request.form['site_name']
        settings.tagline = request.form['tagline']
        settings.footer_text = request.form['footer_text']
        db.session.commit()
        flash('Site settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', settings=settings)

# Messages Management
@app.route('/admin/messages')
@login_required
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/read/<int:id>')
@login_required
def admin_message_read(id):
    message = ContactMessage.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    flash('Message marked as read.', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/delete/<int:id>')
@login_required
def admin_message_delete(id):
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_messages'))

# Contact Form Submission
@app.route('/contact/submit', methods=['POST'])
def contact_submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    contact_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(contact_message)
    db.session.commit()
    
    flash('Thank you for your message! We will get back to you soon.', 'success')
    return redirect(url_for('index') + '#contact')

# ==================== INITIALIZE DATABASE ====================

def init_db():
    with app.app_context():
        if Admin.query.count() == 0:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
        
        if HeroSection.query.count() == 0:
            hero = HeroSection()
            db.session.add(hero)
        
        if AboutSection.query.count() == 0:
            about = AboutSection(
                content="Samuella Bennie Coffie is the creative mind behind Akesi's Kreation—a multidisciplinary artist, chromotherapist, and lifelong lover of color. Her journey with art began at age six, when she first picked up a crochet hook and discovered the peace that comes from creating with her hands. Today, she combines her artistic background with her knowledge of chromotherapy to design pieces that do more than beautify—they uplift, calm, and inspire."
            )
            db.session.add(about)
        
        if UniqueFeature.query.count() == 0:
            default_features = [
                UniqueFeature(icon="fa-heart", title="Art Meets Emotion", description="Every piece is crafted with intention—merging art, color, and therapy to inspire emotional balance and self-expression.", order=1),
                UniqueFeature(icon="fa-palette", title="Signature Use of Color", description="We treat color as more than visual beauty. Each shade is chosen for its emotional effect, creating designs that calm, uplift, and energize.", order=2),
                UniqueFeature(icon="fa-hands", title="Handcrafted Excellence", description="Our creations are meticulously made by hand, ensuring precision, texture, and timeless appeal in every detail.", order=3),
                UniqueFeature(icon="fa-tshirt", title="Wearable Art & Beyond", description="From crochet earrings and fascinators to mixed media paintings and wall art, our work transforms artistry into luxury.", order=4),
                UniqueFeature(icon="fa-globe-africa", title="Global Aesthetic with African Soul", description="Rooted in African creativity yet inspired by global art and fashion, we bridge cultures through design and emotion.", order=5),
                UniqueFeature(icon="fa-user", title="Uniqueness as Identity", description="Each piece celebrates individuality—made to remind you that confidence and beauty begin with being authentically yourself.", order=6)
            ]
            for feature in default_features:
                db.session.add(feature)
        
        if Product.query.count() == 0:
            default_products = [
                Product(name="Crochet Earrings", description="Handcrafted earrings that combine traditional techniques with contemporary design.", icon="fa-gem", gradient_from="purple-400", gradient_to="pink-500", order=1),
                Product(name="Fascinators", description="Elegant headpieces that make a statement at any special occasion.", icon="fa-hat-cowboy", gradient_from="blue-400", gradient_to="teal-500", order=2),
                Product(name="Mixed Media Art", description="Wall art and paintings that blend various materials and techniques.", icon="fa-paint-brush", gradient_from="yellow-400", gradient_to="orange-500", order=3)
            ]
            for product in default_products:
                db.session.add(product)
        
        if JourneyMilestone.query.count() == 0:
            default_milestones = [
                JourneyMilestone(year="2011", title="The Spark Ignites", description="A creative journey begins as our founder learns to bead and soon after, to crochet—laying the foundation for a lifelong passion for handcrafted art.", color="purple-700", order=1),
                JourneyMilestone(year="2020", title="Akesi's Kreation is Born", description="The vision becomes reality. Akesi's Kreation is officially launched, combining traditional techniques with a bold, contemporary aesthetic to create wearable art with meaning.", color="pink-600", order=2),
                JourneyMilestone(year="2023", title="Therapeutic Artistry Emerges", description="Grounded in chromotherapy, the brand evolves to embrace art as a tool for emotional well-being.", color="blue-600", order=3),
                JourneyMilestone(year="Today", title="A Purposeful Creative Force", description="Akesi's Kreation continues to grow, uniting art, culture, and wellness to craft pieces that uplift, empower, and inspire.", color="green-600", order=4)
            ]
            for milestone in default_milestones:
                db.session.add(milestone)
        
        if WhyChooseUs.query.count() == 0:
            default_items = [
                WhyChooseUs(icon="fa-hands", title="Handcrafted with Intention", description="Every piece is made by hand, ensuring quality, detail, and uniqueness.", order=1),
                WhyChooseUs(icon="fa-palette", title="Color as Therapy", description="Our designs are created to inspire, uplift, and balance emotions through thoughtful use of color.", order=2),
                WhyChooseUs(icon="fa-tshirt", title="Wearable Art", description="From crochet fashion to fascinators and accessories, our creations are designed to be experienced, not just admired.", order=3),
                WhyChooseUs(icon="fa-user-graduate", title="Creative Expertise", description="Led by Samuella Coffie, a multidisciplinary artist and chromotherapist with years of experience.", order=4),
                WhyChooseUs(icon="fa-globe", title="Global Inspiration, Personal Touch", description="While rooted in African creativity, our designs are influenced by global trends and aesthetics.", order=5)
            ]
            for item in default_items:
                db.session.add(item)
        
        if ContactInfo.query.count() == 0:
            contact = ContactInfo()
            db.session.add(contact)
        
        if SiteSetting.query.count() == 0:
            settings = SiteSetting()
            db.session.add(settings)
        
        db.session.commit()
        print("Database initialized with default data!")

# Create database and tables
with app.app_context():
    db.create_all()
    init_db()

# This is needed for PythonAnywhere
application = app

if __name__ == '__main__':
    app.run(debug=False)