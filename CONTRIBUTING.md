# Contributing to Agent Builder

We welcome contributions to Agent Builder! This document provides guidelines for contributing to the project, whether you're fixing bugs, adding features, improving documentation, or helping with testing.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)
- [Recognition](#recognition)

## Getting Started

### Ways to Contribute

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **📝 Documentation**: Improve guides, examples, and API docs
- **🧪 Testing**: Write tests, report test results
- **💻 Code Contributions**: Fix bugs, implement features
- **🎨 UI/UX Improvements**: Enhance user interface and experience
- **🔧 DevOps**: Improve build processes, CI/CD, deployment
- **🌐 Translations**: Help make the project accessible globally

### First Time Contributors

Looking for something to work on? Check out issues labeled:
- `good-first-issue` - Good for newcomers
- `help-wanted` - We'd love community help
- `documentation` - Documentation improvements needed
- `bug` - Bug fixes needed

## Development Setup

### Prerequisites

Before contributing, ensure you have:
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)  
- **PostgreSQL** (v12 or higher)
- **Git** for version control
- A GitHub account

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
```bash
git clone https://github.com/YOUR_USERNAME/agent-builder.git
cd agent-builder
```

3. **Add upstream remote**:
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/agent-builder.git
```

### Environment Setup

1. **Run the setup script**:
```bash
# Windows
setup.bat

# Linux/MacOS
chmod +x setup.sh
./setup.sh
```

2. **Or set up manually**:
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
cp .env.example .env
# Edit .env with your configuration

# Database setup
createdb agent_builder_dev
python -m alembic upgrade head

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. **Verify setup**:
```bash
# Start backend (in backend/ directory)
uvicorn app.main:app --reload

# Start frontend (in frontend/ directory)
npm start

# Run tests
cd backend && pytest
cd frontend && npm test
```

## Contributing Guidelines

### Branching Strategy

We use **Git Flow** for branch management:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `release/version-number` - Release preparation

### Creating a Feature Branch

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code formatting (no functional changes)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build process, auxiliary tools, etc.

**Examples:**
```bash
feat(workflow): add drag-and-drop component reordering
fix(api): resolve memory leak in document processing
docs(readme): update installation instructions
test(components): add unit tests for LLM engine component
```

### Keeping Your Fork Updated

```bash
git checkout develop
git fetch upstream
git merge upstream/develop
git push origin develop
```

## Code Standards

### Python (Backend)

We use **Black**, **isort**, and **flake8** for code formatting:

```bash
# Format code
black app/
isort app/

# Check linting
flake8 app/

# Run all checks
make lint  # If Makefile exists
```

**Code Style:**
- Maximum line length: 88 characters (Black default)
- Use type hints for function parameters and return values
- Follow PEP 8 naming conventions
- Write docstrings for all public functions and classes

```python
# Good example
async def process_document(
    document_id: str, 
    options: Dict[str, Any]
) -> DocumentProcessingResult:
    """
    Process a document and extract text content.
    
    Args:
        document_id: Unique identifier for the document
        options: Processing configuration options
        
    Returns:
        DocumentProcessingResult containing extracted text and metadata
        
    Raises:
        DocumentNotFoundError: If document doesn't exist
        ProcessingError: If document processing fails
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

We use **ESLint** and **Prettier** for code formatting:

```bash
# Format code
npm run format

# Check linting
npm run lint

# Fix linting issues
npm run lint:fix
```

**Code Style:**
- Use functional components with hooks
- Use TypeScript-style JSDoc for documentation
- Prefer `const` over `let`, avoid `var`
- Use meaningful variable and function names
- Keep components small and focused

```javascript
// Good example
/**
 * Workflow component that handles drag-and-drop functionality
 * @param {Object} props Component properties
 * @param {Array} props.nodes Array of workflow nodes
 * @param {Function} props.onNodesChange Callback for node changes
 * @returns {JSX.Element} Rendered workflow component
 */
const WorkflowBuilder = ({ nodes, onNodesChange }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  
  const handleNodeSelect = useCallback((nodeId) => {
    setSelectedNode(nodeId);
  }, []);
  
  return (
    <div className="workflow-builder">
      {/* Component implementation */}
    </div>
  );
};
```

### CSS/Styling

- Use **Tailwind CSS** for styling
- Follow mobile-first responsive design
- Use semantic class names for custom CSS
- Maintain consistent spacing and color schemes

```css
/* Good example - custom CSS when needed */
.workflow-canvas {
  @apply relative w-full h-full bg-gray-50 overflow-hidden;
}

.component-node {
  @apply rounded-lg border-2 border-gray-200 bg-white shadow-sm;
  @apply hover:shadow-md transition-shadow duration-200;
}

.component-node--selected {
  @apply border-blue-500 ring-2 ring-blue-200;
}
```

## Testing Requirements

### Backend Testing

**Required for all contributions:**
- Unit tests for new functions/classes
- Integration tests for API endpoints
- Coverage should not decrease

```python
# Example unit test
import pytest
from app.services.document_service import DocumentService

@pytest.fixture
def document_service():
    return DocumentService()

@pytest.mark.asyncio
async def test_extract_text_from_pdf(document_service, sample_pdf):
    result = await document_service.extract_text(sample_pdf)
    
    assert result.success is True
    assert len(result.text) > 0
    assert result.page_count > 0

# Example integration test
@pytest.mark.asyncio
async def test_upload_document_api(client):
    with open("tests/fixtures/sample.pdf", "rb") as f:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("sample.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 201
    assert "id" in response.json()
```

**Running tests:**
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_document_service.py

# Run tests matching pattern
pytest -k "test_upload"
```

### Frontend Testing

**Required for all contributions:**
- Component unit tests
- Integration tests for complex features
- Accessibility tests

```javascript
// Example component test
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import WorkflowBuilder from '../WorkflowBuilder';

describe('WorkflowBuilder', () => {
  test('renders without crashing', () => {
    render(<WorkflowBuilder nodes={[]} onNodesChange={jest.fn()} />);
    expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument();
  });

  test('handles node selection', async () => {
    const user = userEvent.setup();
    const mockOnNodesChange = jest.fn();
    
    render(
      <WorkflowBuilder 
        nodes={[mockNode]} 
        onNodesChange={mockOnNodesChange} 
      />
    );

    await user.click(screen.getByTestId('node-1'));
    
    expect(screen.getByTestId('node-1')).toHaveClass('selected');
  });

  test('is accessible', async () => {
    const { container } = render(
      <WorkflowBuilder nodes={[]} onNodesChange={jest.fn()} />
    );
    
    // Check for accessibility violations
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

**Running tests:**
```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test WorkflowBuilder.test.js
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
```bash
# Backend
cd backend && pytest

# Frontend  
cd frontend && npm test
```

2. **Check code formatting**:
```bash
# Backend
black app/ && isort app/ && flake8 app/

# Frontend
npm run lint && npm run format
```

3. **Update documentation** if needed
4. **Add tests** for new functionality
5. **Update CHANGELOG.md** if applicable

### Submitting Pull Request

1. **Push your branch**:
```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request** on GitHub with:
   - **Clear title** following our naming convention
   - **Detailed description** of changes
   - **Link to related issues** (fixes #123)
   - **Screenshots/GIFs** for UI changes
   - **Testing instructions**

3. **Pull Request Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix/feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots or GIFs here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No merge conflicts
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** by reviewers if needed
4. **Approval** required before merge

**Review criteria:**
- Code quality and style
- Test coverage and quality
- Documentation completeness
- Performance impact
- Security considerations
- User experience impact

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 91]
- Version: [e.g., 1.0.0]

**Additional context**
Any other context about the problem
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of what you want to happen

**Describe alternatives you've considered**
Alternative solutions or features considered

**Additional context**
Add any other context or screenshots
```

### Security Issues

**Do not** create public issues for security vulnerabilities.
Instead, email: security@agent-builder.com

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

**Key principles:**
- Be respectful and inclusive
- Be collaborative and constructive  
- Focus on what's best for the community
- Show empathy towards other community members

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Discord**: Real-time chat (link in README)
- **Email**: Direct contact for sensitive issues

### Getting Help

**Before asking for help:**
1. Check existing documentation
2. Search existing issues/discussions  
3. Try debugging with our troubleshooting guide

**When asking for help:**
- Provide clear problem description
- Include relevant code snippets
- Share error messages in full
- Mention your environment details

## Recognition

### Contributors

We recognize contributors in several ways:

- **Contributors section** in README.md
- **Release notes** mention significant contributions
- **GitHub contributors** page
- **Special recognition** for major contributions

### Contribution Types

We value all types of contributions:
- 💻 Code contributions
- 📖 Documentation improvements
- 🐛 Bug reports and testing
- 💡 Feature ideas and feedback
- 🎨 Design and UX contributions
- 🌐 Translation and localization
- 📢 Community building and outreach

### Maintainer Recognition

Active contributors may be invited to join the maintainer team with:
- Commit access to the repository
- Review and merge privileges
- Participation in project decisions
- Recognition as a core team member

## Release Process

### Version Numbers

We use [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features (backward compatible)
- **Patch** (1.1.1): Bug fixes (backward compatible)

### Release Schedule

- **Patch releases**: As needed for critical fixes
- **Minor releases**: Monthly or when significant features are ready
- **Major releases**: Quarterly or when breaking changes accumulate

### Pre-release Testing

Before major releases:
1. **Alpha testing**: Internal testing by maintainers
2. **Beta testing**: Community testing with pre-release versions
3. **Release candidate**: Final testing before stable release

## Advanced Contributing

### Setting up Development Environment

**IDE Recommendations:**
- **VS Code** with extensions:
  - Python
  - ES7+ React/Redux/React-Native snippets
  - Prettier - Code formatter
  - ESLint
  - Tailwind CSS IntelliSense

**Recommended VS Code Settings:**
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

### Database Development

**Creating Migrations:**
```bash
cd backend
# Create new migration
python -m alembic revision --autogenerate -m "Description of changes"

# Apply migration
python -m alembic upgrade head
```

**Testing with Different Databases:**
```bash
# Test with SQLite (for quick testing)
export DATABASE_URL="sqlite:///./test.db"

# Test with PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost:5432/testdb"
```

### Performance Testing

**Backend Performance:**
```bash
# Install testing tools
pip install locust

# Run performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

**Frontend Performance:**
```bash
# Bundle analysis
npm run build -- --analyze

# Lighthouse CI
npm install -g @lhci/cli
lhci autorun
```

### Documentation Development

**Building Documentation:**
```bash
# Install documentation tools
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

Thank you for contributing to Agent Builder! Your contributions help make this project better for everyone. 🚀

---

*This contributing guide is itself open to contributions! If you see ways to improve it, please submit a pull request.*