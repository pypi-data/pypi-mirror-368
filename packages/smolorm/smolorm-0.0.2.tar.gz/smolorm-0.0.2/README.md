# smolorm

A **tiny, minimalistic ORM** for Python — built to make SQL feel simple, explicit, and fun.  
`smolorm` doesn’t try to hide SQL; it helps you write it fluently, keep full control over queries, and understand exactly what’s happening under the hood.  

Perfect for learning SQL, prototyping, or building small apps without dragging in a massive framework.

## Features

- **Fluent API**: `select().where().run()` style chaining  
- **CRUD operations**: `.create()`, `.update()`, `.delete()`  
- **Model-based**: Define tables by subclassing `SqlModel`  
- **Dynamic expressions** with `col()` for building WHERE clauses  
- **Table management**: Create and drop tables directly from models  
- **No hidden magic**: SQL is generated transparently, no ORM black box

## Installation

```bash
pip install smolorm

