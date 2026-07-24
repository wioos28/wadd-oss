JavaScript is a versatile programming language primarily used for web development.

## Core Concepts

JavaScript was created by Brendan Eich in 1995 and has evolved into one of the most popular programming languages in the world.

### Variables and Data Types

```javascript
// Variables
let name = "Alice";        // String
const age = 25;            // Number
let isStudent = true;      // Boolean
let scores = [90, 85, 92]; // Array
let person = {             // Object
    name: "Bob",
    age: 30
};
```

### Functions

```javascript
// Function declaration
function greet(name) {
    return `Hello, ${name}!`;
}

// Arrow function
const add = (a, b) => a + b;

// Async function
async function fetchData(url) {
    const response = await fetch(url);
    return await response.json();
}
```

## JavaScript Ecosystem

### Frontend Frameworks
- **React**: Component-based UI library by Facebook
- **Vue.js**: Progressive framework for building UIs
- **Angular**: Full-featured framework by Google

### Backend Runtime
- **Node.js**: JavaScript runtime built on Chrome's V8 engine
- **Deno**: Secure runtime for JavaScript and TypeScript
- **Bun**: Fast JavaScript runtime and toolkit

### Package Management
- **npm**: Node Package Manager
- **yarn**: Fast, reliable package manager
- **pnpm**: Efficient package manager

## Modern JavaScript Features (ES6+)

```javascript
// Destructuring
const { name, age } = person;

// Spread operator
const newArray = [...oldArray, newItem];

// Optional chaining
const city = user?.address?.city;

// Nullish coalescing
const value = input ?? "default";
```

## JavaScript Performance Tips

1. Use `const` and `let` instead of `var`
2. Avoid global variables
3. Use event delegation
4. Optimize DOM access
5. Use Web Workers for heavy computations
