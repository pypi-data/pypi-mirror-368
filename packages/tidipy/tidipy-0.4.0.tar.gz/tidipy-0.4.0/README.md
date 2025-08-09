# TiDIpy

## Index

- [Intro](#intro)  
- [In the spirit of real DI](#in-the-spirit-of-real-di)  
- [Scopes and lifetime management](#scopes-and-lifetime-management)  
  - [A tree of scopes](#a-tree-of-scopes)  
- [Working with scope context](#working-with-scope-context)  
- [Resolve by id](#resolve-by-id)  
- [Integration with starlette/fastapi](#integration-with-starlettefastapi)  
- [API Reference](#api-reference)

## Intro

TiDIpy—short for Timber Dependency Injection Python—is a minimalist, opinionated dependency injection framework created by me, Timber. It emphasizes simplicity, ease of use, and a principled approach to DI.

## In the spirit of real DI

The essence of dependency injection is to invert the direction of dependency: the client specifies what type of dependencies it requires, while someone else decides which concrete instances to provide. Many DI frameworks blur this distinction by introducing configuration logic directly into the client—who should only declare its dependencies, not manage them. While this can seem convenient, it undermines the core value of dependency injection.

TiDIpy maintains this separation strictly. Consider the following client:
```
class MyClient:
    def __init__(self, dependency: MyDependency):
        ... 
```
No TiDIpy-specific elements are required in MyClient. Instead, composition is handled externally in a dedicated composer function:
```
@composer
def my_client() -> MyClient:
    return MyClient(MyDependency())
```
This keeps the client clean and focused and ensures that wiring and instantiation remain a separate responsibility of the composition root.

Keeping dependency composition explicitly separate is the core principle of DI—but it does come with the trade-off of writing a bit more code. TiDIpy aims to make defining the composition root as convenient as possible. One key feature that helps with this is _auto composition_:
```
auto_compose(MyClient)
```
This allows TiDIpy to automatically resolve and compose the dependencies in many cases, reducing boilerplate while preserving separation of concerns.

## Scopes and lifetime management

Composition isn't just about specifying how dependencies are created and connected—it's also about managing _when_ they are instantiated and cleaned up. Not every object in the dependency graph needs to be created upfront, and clients should stay unaware of the timing or lifecycle of their dependencies.

TiDIpy handles this through _scopes_. Every composer in TiDIpy is associated with a scope type—by default, this is `root`. You can assign a custom scope like this:
```
@composer(scope_type='request')
def my_dependency() -> MyDependency:
    ...
```
This means `MyDependency` will only be available within scopes of type `request`. To resolve it during a specific request, you'd do:
```
ensure_scope(scope_id='my-request', scope_type='request')
resolver = get_resolver('my-request')
resolver(MyDependency)
```
When the request ends, the scope—and any dependencies created within it—can be explicitly cleared:
```
clear_scope('my-request')
```
This ensures that scoped dependencies are properly cleaned up, giving you fine-grained control over object lifetimes.

### A tree of scopes

Each scope in the system has a parent scope. If no parent is explicitly defined, the scope defaults to having `root` as its parent. Scopes form a hierarchy, and any scope can access the dependencies registered in its own context as well as those of all its ancestors.

Here's how you can define dependencies in different scopes:
```
auto_compose(DependencyA)  # Registered in the root scope
auto_compose(DependencyB, scope_type='tenant')  # Registered in tenant-level scope
auto_compose(DependencyC, scope_type='request')  # Registered in request-level scope
```

Now we can start a request scope _within_ a specific tenant scope:
```
ensure_scope(scope_id='my-tenant', scope_type='tenant')  # Create tenant scope
ensure_scope(scope_id='my-request', scope_type='request', parent_id='my-tenant')  # Create request scope with tenant as parent

resolver = get_resolver('my-request')  # Get a resolver for the request scope
```
Once the scopes are in place, you can resolve dependencies from the request scope. The resolver will automatically traverse up the scope hierarchy as needed:
```
resolver(DependencyA)  # Resolved from root scope
resolver(DependencyB)  # Resolved from tenant scope
resolver(DependencyC)  # Resolved from request scope

```
## Working with scope context

A common scenario in dependency injection is when a client depends on an interface that has multiple implementations. In such cases, the composition logic must decide which concrete implementation to provide.
```
class Repository(ABC):
    @abstractmethod
    get_by_id(id: str):
        ...

class InMemoryRepository(Repository):
    ...
    

class PostgresRepository(Repository):
    ...
```

If both `InMemoryRepository` and `PostgresRepository` have their own composers, then the type Repository becomes ambiguous—TiDIpy won’t know which one to resolve by default.

You can use _scope context_ — key-value tags that express context-specific choices.
```
@composer(stage='prod')
def postgres_repository() -> PostgresRepository:
    return PostgresRepository()

@composer(stage='test')
def in_memory_repository() -> InMemoryRepository:
    return InMemoryRepository()
```
The line `@composer(stage='prod')` means that if the key `stage` is part of the scope context, this composer will only
be considered if it has value `prod`.

We add context to our scope with:
```
ensure_scope(scope_id='app', scope_type='app', context={'stage': 'test'})
```
This now means that `resolve(Repository)` will resolve to an `InMemoryRepository`.


## Resolve by id

Sometimes, you need multiple composers that return the same type but represent different roles or configurations. By assigning an explicit id to each composer, you can resolve the exact one you need without ambiguity.

```
@composer(id='primary-db')
def primary_connection() -> DatabaseConnection:
    return DatabaseConnection(dsn='postgresql://primary.db.local')

@composer(id='analytics-db')
def analytics_connection() -> DatabaseConnection:
    return DatabaseConnection(dsn='postgresql://analytics.db.local')
```
Here, both composers return `DatabaseConnection`, but they're configured for different purposes. Resolving `DatabaseConnection` is ambiguous.

Instead, you can resolve them explicitly by ID:
```
resolve(DatabaseConnection, id='primary-db')
```
Since IDs are unique, this guarantees an unambiguous resolution.

## Integration with starlette/fastapi

See  [FastAPI example](https://github.com/timberkerkvliet/TiDIpy/blob/main/examples/fastapi_app.py).

## API reference

Everything can be imported from the root of the package:

```
from TiDIpy import composer, auto_compose, ensure_scope, clear_scope, reset, get_resolver, scan
```

### composer

`composer` is a function decorator that takes as arguments:
* `id: str`: the id of this dependency
* `scope_type: str`: the types of scopes in which it is available
* `kwargs: str | set[str]`: the values in the scope context for which this dependency is available

### auto_compose

`auto_compose` is a function that takes a class as its first arguments and will auto compose based on the typing in its `__init__`. Apart from this argument, it has the same arguments as `composer`.

### ensure_scope

`ensure_scope` is a function checks that a scope with the given properties already exists and if not creates one. It takes as arguments:
* `scope_id: str` the target scope
* `scope_type: str` the type this scope should have
* `parent_id: str` the ID of the parent scope (by default `root`)
* `context: Optional[dict[str,str]]` context of the scope (by default empty)

### clear_scope

`clear_scope` is a function that clears a scope and all of its children. It has `scope_id: str` as argument.

### reset

`reset` is a function that resets TiDI completely. It clears all scopes and forgets all registered composers.

### get_resolver

`get_resolver` is a function that gets the resolver of a certain scope. It takes `scope_id: str` as argument to indicate the target scope.

### scan

`scan` is a function that scans a python module for composers. It takes a module as an argument:

```
from my_project import composition_root

scan(composition_root)
```
