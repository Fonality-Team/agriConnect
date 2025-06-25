# AgriConnect 🌾

A modern web platform connecting farmers, suppliers, and buyers in the agricultural ecosystem. Built with Flask and designed to facilitate direct trade relationships between agricultural stakeholders.

## 🚀 Features

- **Farmer Marketplace**: Direct sales platform for agricultural products
- **Supplier Network**: Connect with agricultural input suppliers
- **Buyer Portal**: Easy procurement for businesses and consumers
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Modern UI**: Clean, accessible interface for all users

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.1 (Python 3.12+)
- **Database**: SQLAlchemy with SQLite (development)
- **Frontend**: Tailwind CSS 4.1.10
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Package Management**: UV (Python), PNPM (Node.js)
- **Containerization**: Docker

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+ and PNPM
- UV package manager
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agriConnect
   ```

2. **Set up Python environment**
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install Python dependencies
   uv sync
   ```

3. **Install Node.js dependencies**
   ```bash
   pnpm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Build CSS assets**
   ```bash
   pnpm run build
   ```

6. **Initialize the database**
   ```bash
   uv run python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

7. **Run the application**
   ```bash
   uv run python run.py
   ```

Visit `http://localhost:5000` to see the application.

### Development Workflow

- **Watch CSS changes**: `pnpm run watch`
- **Build production CSS**: `pnpm run build`
- **Run Flask app**: `uv run python run.py`

## 🐳 Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -t agriconnect .

# Run the container
docker run -p 5000:5000 \
  -e SECRET_KEY=your_secret_key \
  -e DATABASE_URL=sqlite:///./app.db \
  -v $(pwd)/instance:/app/instance \
  agriconnect
```

### Using Docker Compose (recommended)

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your_secret_key_here
      - DATABASE_URL=sqlite:///./app.db
      - DEBUG=False
    volumes:
      - ./instance:/app/instance
      - uploads:/app/app/static/uploads
    restart: unless-stopped

volumes:
  uploads:
```

Run with: `docker-compose up -d`

## 📁 Project Structure

```
agriConnect/
├── app/                    # Main application package
│   ├── __init__.py        # App factory
│   ├── core/              # Core functionality
│   │   └── config.py      # Configuration management
│   ├── extensions.py      # Flask extensions initialization
│   ├── models/            # Database models
│   ├── static/            # Static assets
│   │   └── css/           # Stylesheets
│   ├── templates/         # Jinja2 templates
│   │   ├── base.html      # Base template
│   │   └── main/          # Main blueprint templates
│   └── views/             # Application views/routes
│       ├── __init__.py    # Blueprint registration
│       └── main/          # Main blueprint
├── instance/              # Instance-specific files (databases, uploads)
├── .env                   # Environment variables
├── .python-version        # Python version specification
├── Dockerfile            # Docker configuration
├── Makefile              # Build automation
├── package.json          # Node.js dependencies
├── pyproject.toml        # Python project configuration
└── run.py                # Application entry point
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_very_secret_key_here
DEBUG=True
```

### Production Settings

For production deployment:
- Set `DEBUG=False`
- Use a strong, unique `SECRET_KEY`
- Configure a production database (PostgreSQL recommended)
- Set up proper logging
- Configure HTTPS

## 🧪 Testing

```bash
# Run tests (when implemented)
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

## 🔧 Development Commands

```bash
# Compile requirements
make compile

# Build CSS for production
pnpm run build

# Watch CSS during development
pnpm run watch

# Format code (when configured)
uv run ruff format .

# Lint code (when configured)
uv run ruff check .
```

## 🚀 Deployment

### Production Checklist

- [ ] Set environment variables properly
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up backup strategy
- [ ] Configure monitoring
- [ ] Set up CI/CD pipeline

### Recommended Production Stack

- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Caching**: Redis
- **Monitoring**: Sentry, Prometheus

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Write tests for new features
- Update documentation as needed
- Ensure responsive design for new UI components

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Link to docs when available]
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Contact**: [Your contact information]

## 🎯 Roadmap

- [ ] User authentication and profiles
- [ ] Product catalog and search
- [ ] Order management system
- [ ] Payment integration
- [ ] Mobile app development
- [ ] API development
- [ ] Multi-language support

---

**AgriConnect** - Connecting agricultural communities for sustainable growth 🌱
