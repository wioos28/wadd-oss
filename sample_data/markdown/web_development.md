# Web Development

## 1. HTML/CSS Fundamentals

### HTML5 Semantic Elements
```html
<header>    <!-- Header section -->
<nav>       <!-- Navigation -->
<main>      <!-- Main content -->
<article>   <!-- Article content -->
<section>   <!-- Section -->
<aside>     <!-- Sidebar -->
<footer>    <!-- Footer -->
```

### CSS Flexbox
```css
.container {
    display: flex;
    justify-content: space-between; /* Main axis */
    align-items: center;            /* Cross axis */
    flex-wrap: wrap;
}

.item {
    flex: 1;              /* Grow */
    flex-shrink: 0;       /* Don't shrink */
    flex-basis: 200px;    /* Base size */
}
```

### CSS Grid
```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 20px;
}

.item {
    grid-column: span 2;
    grid-row: 1 / 3;
}
```

## 2. JavaScript

### ES6+ Features
```javascript
// Destructuring
const { name, age } = person;
const [first, ...rest] = array;

// Spread/Rest
const newArray = [...oldArray, newItem];
const sum = (...numbers) => numbers.reduce((a, b) => a + b, 0);

// Optional chaining
const street = user?.address?.street;

// Nullish coalescing
const value = null ?? 'default';

// Async/Await
async function fetchData() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}
```

### Promises
```javascript
// Promise
const promise = new Promise((resolve, reject) => {
    if (success) resolve(data);
    else reject(error);
});

// Promise.all - all must succeed
const results = await Promise.all([p1, p2, p3]);

// Promise.race - first to complete
const result = await Promise.race([p1, p2, p3]);

// Promise.allSettled - wait for all
const results = await Promise.allSettled([p1, p2, p3]);
```

## 3. React

### Components
```jsx
// Function Component
function Counter({ initialCount }) {
    const [count, setCount] = useState(initialCount);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(c => c + 1)}>
                Increment
            </button>
        </div>
    );
}

// Class Component (legacy)
class Counter extends React.Component {
    state = { count: 0 };
    
    render() {
        return <p>{this.state.count}</p>;
    }
}
```

### Hooks
```jsx
// useState
const [state, setState] = useState(initialValue);

// useEffect
useEffect(() => {
    fetchData();
    return () => cleanup(); // Cleanup
}, [dependency]); // Dependency array

// useContext
const value = useContext(MyContext);

// useRef
const ref = useRef(null);

// useMemo / useCallback
const memoizedValue = useMemo(() => compute(a, b), [a, b]);
const memoizedCallback = useCallback(() => doSomething(a), [a]);
```

### State Management
- **Redux**: Predictable state container
- **Context API**: Built-in React context
- **Zustand**: Lightweight alternative
- **Jotai**: Atomic state
- **Recoil**: Facebook's state management

## 4. Node.js

### Express.js
```javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Routes
app.get('/api/users', async (req, res) => {
    const users = await User.find();
    res.json(users);
});

app.post('/api/users', async (req, res) => {
    const user = await User.create(req.body);
    res.status(201).json(user);
});

// Error handling
app.use((err, req, res, next) => {
    res.status(500).json({ error: err.message });
});

app.listen(3000);
```

### Middleware Pattern
```javascript
// Custom middleware
const authMiddleware = (req, res, next) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ error: 'Unauthorized' });
    
    try {
        const decoded = jwt.verify(token, SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

// Apply to routes
app.get('/protected', authMiddleware, (req, res) => {
    res.json({ message: 'Protected data' });
});
```

## 5. TypeScript

### Types
```typescript
// Basic types
let name: string = 'John';
let age: number = 30;
let active: boolean = true;

// Arrays
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ['a', 'b'];

// Objects
interface User {
    id: number;
    name: string;
    email?: string; // Optional
}

// Union types
type ID = string | number;

// Generic
function identity<T>(arg: T): T {
    return arg;
}
```

### Classes & Interfaces
```typescript
interface Printable {
    print(): void;
}

class Document implements Printable {
    constructor(public title: string) {}
    
    print(): void {
        console.log(this.title);
    }
}

// Abstract class
abstract class Shape {
    abstract area(): number;
    
    describe(): string {
        return `Area: ${this.area()}`;
    }
}
```

## 6. Build Tools

### Webpack
```javascript
module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: 'babel-loader',
            },
        ],
    },
};
```

### Vite
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
    },
});
```

## 7. Testing

### Jest
```javascript
// Unit test
describe('Calculator', () => {
    test('adds 1 + 2', () => {
        expect(add(1, 2)).toBe(3);
    });
});

// Async test
test('fetches data', async () => {
    const data = await fetchData();
    expect(data).toBeDefined();
});
```

### React Testing Library
```jsx
import { render, screen, fireEvent } from '@testing-library/react';

test('increments counter', () => {
    render(<Counter />);
    fireEvent.click(screen.getByText('Increment'));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

## 8. Performance Optimization

### Code Splitting
```javascript
// React.lazy
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// Dynamic import
const module = await import('./module');
```

### Memoization
```jsx
// React.memo
const MemoizedComponent = React.memo(Component);

// useMemo
const memoizedValue = useMemo(() => compute(a, b), [a, b]);

// useCallback
const memoizedCallback = useCallback(() => doSomething(a), [a]);
```

### Bundle Analysis
```bash
npm run build -- --analyze
# or
npx webpack-bundle-analyzer stats.json
```
