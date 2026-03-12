# 🤝 Contribution Guide

Merci de vouloir contribuer au **EPI Detection System**! Ce document explique comment participer.

---

## 📋 Table des Matières

1. [Code of Conduct](#-code-of-conduct)
2. [Getting Started](#-getting-started)
3. [Development Setup](#-development-setup)
4. [Making Changes](#-making-changes)
5. [Testing](#-testing)
6. [Submitting Changes](#-submitting-changes)
7. [Coding Standards](#-coding-standards)
8. [Resources](#-resources)

---

## 🎯 Code of Conduct

Nous nous engageons à fournir un environnement accueillant et inclusif.

### Notre Engagement

- ✅ Être respectueux des autres
- ✅ Accepter les critiques constructives
- ✅ Se concentrer sur ce qui est mieux pour la communauté
- ✅ Être patient et compréhensif

### Comportements Inacceptables

- ❌ Harcèlement ou langage offensant
- ❌ Attaques personnelles
- ❌ Commentaires discriminatoires
- ❌ Spamming ou trolling

---

## 🚀 Getting Started

### 1. Fork le Dépôt

```bash
# Sur GitHub: Click "Fork" button
```

### 2. Clone Localement

```bash
git clone https://github.com/YOUR_USERNAME/EPI-DETECTION-PROJECT.git
cd EPI-DETECTION-PROJECT
git remote add upstream https://github.com/ORIGINAL_OWNER/EPI-DETECTION-PROJECT.git
```

### 3. Créer une Branche

```bash
git checkout -b feature/my-amazing-feature
# ou
git checkout -b fix/issue-123
```

---

## 💻 Development Setup

### 1. Environnement Virtuel

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
```

### 2. Dépendances

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Pour dev tools
```

### 3. Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### 4. Vérifier Config

```bash
python check_system.py
```

---

## ✏️ Making Changes

### Types de Contributions

#### 🐛 Bug Fixes
```bash
git checkout -b fix/issue-description
# Fixer le bug
# Ajouter tests
# Commit et push
```

#### ✨ Features
```bash
git checkout -b feature/new-feature
# Implémenter feature
# Ajouter tests & docs
# Commit et push
```

#### 📚 Documentation
```bash
git checkout -b docs/improve-docs
# Mettre à jour docs
# Vérifier Markdown
# Commit et push
```

#### 🧹 Refactoring
```bash
git checkout -b refactor/improve-code
# Refactoriser code
# Conserver tests passants
# Commit et push
```

### Commit Messages

Format: `<type>: <description>`

```bash
git commit -m "feat: add dark mode toggle"
git commit -m "fix: webcam not detected on Windows"
git commit -m "docs: improve API documentation"
git commit -m "refactor: simplify detection logic"
git commit -m "test: add unit tests for database"
```

### Commit Types

- `feat`: Nouvelle feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (pas de logic change)
- `refactor`: Code restructure
- `test`: Ajouter/modifier tests
- `chore`: Build, dependencies, etc.
- `perf`: Performance improvement

---

## 🧪 Testing

### Run Tests

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=app tests/

# Test spécifique
pytest tests/test_detection.py::test_yolov5_inference

# Verbeux
pytest -v
```

### Écrire des Tests

```python
# tests/test_example.py
import pytest
from app.detection import EPIDetector

def test_detector_initialization():
    """Test que le détecteur s'initialise correctement"""
    detector = EPIDetector()
    assert detector is not None
    assert detector.model is not None

def test_detection_format():
    """Test le format de résultat de détection"""
    detector = EPIDetector()
    # Mock image
    result = detector.detect(mock_image)
    
    assert 'detections' in result
    assert 'fps' in result
    assert 'inference_time_ms' in result
```

### Coverage Target

Minimum: **80%**

```bash
pytest --cov=app --cov-report=html tests/
# Ouvrir htmlcov/index.html
```

---

## 📤 Submitting Changes

### 1. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push Your Changes

```bash
git push origin feature/my-amazing-feature
```

### 3. Open Pull Request

Sur GitHub:
1. Click "Compare & pull request"
2. Remplir template PR
3. Ajouter description claire
4. Reference issues: "Fixes #123"
5. Soumettre

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Related Issues
Fixes #123

## Testing
- [ ] Tested locally
- [ ] Tests added/updated
- [ ] No test regressions

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### PR Review Process

1. Minimum 1 review required
2. Tests must pass (CI/CD)
3. No conflicts with main
4. Approvals before merge

---

## 🎨 Coding Standards

### Python

```python
# PEP 8 compliant
# Format with black if available: black app/

# Good
def detect_epi(image: np.ndarray) -> dict:
    """Detect EPI in image.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        dict: Detection results
    """
    results = self.model(image)
    return self._format(results)

# Bad
def detect(img):
    r=self.m(img)
    return r
```

### JavaScript

```javascript
// Use camelCase
// Comments for complex logic

// Good
async function detectEPI(imageSrc) {
  try {
    const response = await fetch('/api/detect', {
      method: 'POST',
      body: JSON.stringify({image: imageSrc})
    })
    return await response.json()
  } catch (error) {
    console.error('Detection failed:', error)
    throw error
  }
}

// Bad
async function DetectEPI(img){let r=await fetch('/api/detect',{method:'POST',body:JSON.stringify({image:img})});return r.json()}
```

### Documentation

```python
def my_function(param1: str, param2: int) -> bool:
    """
    One-line summary.
    
    Longer description if needed.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When something is invalid
        
    Example:
        >>> result = my_function("test", 42)
        >>> assert result is True
    """
    pass
```

---

## 🏆 Areas for Contribution

### High Priority 🔴
- [ ] Unit tests (80%+ coverage target)
- [ ] CI/CD pipeline
- [ ] Performance optimization
- [ ] Security hardening

### Medium Priority 🟡
- [ ] UI/UX improvements
- [ ] Documentation
- [ ] Bug fixes
- [ ] Code refactoring

### Low Priority 🟢
- [ ] Feature requests
- [ ] Code cleanup
- [ ] Typo fixes
- [ ] Comment improvements

---

## 🐛 Bug Reports

### Before Filing

1. Check existing issues
2. Reproduce the bug
3. Collect error details

### Format

```markdown
**Describe the bug**
Clear description of what's wrong

**To Reproduce**
1. Step 1
2. Step 2
3. ...

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.13.1]
- Flask: [e.g., 2.3.0]

**Error output**
```
Error traceback here
```

**Additional context**
Screenshots, logs, etc.
```

---

## 🆕 Feature Requests

```markdown
**Description**
What feature would you like?

**Use case**
Why do you need this?

**Proposed solution**
How should it work?

**Alternative solutions**
Other approaches considered?

**Additional context**
Examples, references, etc.
```

---

## 📚 Resources

### Documentation
- [README](README.md)
- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture/overview.md)
- [API Docs](docs/api/documentation.md)

### Tools
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Workflow](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
- [Semantic Versioning](https://semver.org/)

### Community
- GitHub Issues: [Report bugs](../../issues)
- GitHub Discussions: [Ask questions](../../discussions)
- Pull Requests: [Submit changes](../../pulls)

---

## 🎓 Learning Resources

### YOLOv5
- [YOLOv5 GitHub](https://github.com/ultralytics/yolov5)
- [YOLOv5 Docs](https://docs.ultralytics.com)

### Flask
- [Flask Documentation](https://flask.palletsprojects.com)
- [Flask Best Practices](https://flask.palletsprojects.com/best_practices)

### PyTorch
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

### Web Development
- [MDN Web Docs](https://developer.mozilla.org/)
- [W3C Standards](https://www.w3.org/)

---

## ✅ Contribution Checklist

- [ ] Fork du dépôt
- [ ] Branch créée
- [ ] Code développé
- [ ] Tests écrits
- [ ] Tests passants
- [ ] Documentation mise à jour
- [ ] Commits propres
- [ ] PR ouverte
- [ ] Description complétée
- [ ] Réponse aux reviews

---

## 🙏 Thank You!

Merci de contribuer! Chaque contribution aide à améliorer EPI Detection System pour tous.

---

**Questions?** 💬 Ouvrez une [GitHub Discussion](../../discussions)

**Found a bug?** 🐛 Créez une [GitHub Issue](../../issues)

---

*Last Updated: January 9, 2026*
