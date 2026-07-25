# Software Engineering

## 1. Development Methodologies

### Waterfall
- Sequential phases
- Requirements → Design → Implementation → Testing → Deployment
- Pros: Clear structure, documentation
- Cons: Inflexible, late feedback

### Agile
- Iterative development
- Sprints (1-4 weeks)
- Continuous feedback
- Working software over documentation

### Scrum Framework
| Role | Responsibility |
|------|----------------|
| Product Owner | Backlog management, priorities |
| Scrum Master | Process facilitation, impediment removal |
| Team | Self-organizing, cross-functional |

**Ceremonies:**
- Sprint Planning
- Daily Standup
- Sprint Review
- Sprint Retrospective

### Kanban
- Visual workflow (Kanban board)
- WIP limits
- Continuous flow
- Pull-based system

## 2. Git Workflow

### Branching Strategies
```
main (production)
  |
  +-- develop (integration)
      |
      +-- feature/user-auth
      +-- feature/payment
      |
      +-- release/v1.0
      |
      +-- hotfix/critical-bug
```

### Git Commands
```bash
# Branching
git branch feature/new-feature
git checkout -b feature/new-feature
git checkout -b feature/new-feature origin/develop

# Staging & Commit
git add .
git commit -m "feat: add user authentication"
git push origin feature/new-feature

# Merging
git checkout develop
git merge --no-ff feature/new-feature

# Rebasing
git checkout feature/new-feature
git rebase develop
```

### Commit Message Convention
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** feat, fix, docs, style, refactor, test, chore

## 3. Code Quality

### Clean Code Principles
1. **Meaningful Names**: Intention-revealing names
2. **Small Functions**: Do one thing well
3. **DRY**: Don't Repeat Yourself
4. **KISS**: Keep It Simple, Stupid
5. **YAGNI**: You Aren't Gonna Need It

### SOLID Principles
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

### Code Smells
- Long methods
- Large classes
- Duplicated code
- Long parameter lists
- Dead code
- Feature envy

### Refactoring Techniques
- Extract Method
- Extract Class
- Rename
- Move Method
- Replace Temp with Query
- Introduce Parameter Object

## 4. Testing

### Test Pyramid
```
         /\
        /  \  E2E Tests
       /    \  (Few)
      /------\
     /        \  Integration Tests
    /          \  (Some)
   /------------\
  /              \  Unit Tests
 /                \  (Many)
/------------------\
```

### Testing Types
| Type | Purpose | Example |
|------|---------|---------|
| Unit | Test individual units | Function, class method |
| Integration | Test component interaction | API + Database |
| E2E | Test complete workflow | User login flow |
| Performance | Test speed, load | Stress testing |
| Security | Test vulnerabilities | Penetration testing |

### Test-Driven Development (TDD)
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code quality

## 5. Design Patterns

### Creational
- **Singleton**: Single instance
- **Factory**: Create objects without specifying class
- **Builder**: Construct complex objects step by step

### Structural
- **Adapter**: Interface compatibility
- **Decorator**: Add behavior dynamically
- **Facade**: Simplify complex subsystem

### Behavioral
- **Observer**: Publish-subscribe
- **Strategy**: Interchangeable algorithms
- **Command**: Encapsulate requests

## 6. API Design

### RESTful Principles
- Resource-based URLs
- HTTP methods for operations
- Stateless
- Uniform interface

### API Versioning
```
/api/v1/users
/api/v2/users
```

### Error Handling
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

## 7. Documentation

### Types
- **README**: Project overview
- **API Documentation**: Endpoints, parameters
- **Code Comments**: Explain complex logic
- **Architecture Docs**: System design
- **Changelog**: Version history

### Documentation Tools
- Swagger/OpenAPI for APIs
- JSDoc/Sphinx for code
- Mermaid for diagrams
- MkDocs/Docusaurus for sites
