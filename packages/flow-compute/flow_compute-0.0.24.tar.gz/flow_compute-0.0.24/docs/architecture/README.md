# Architecture

Technical documentation on Flow's design and implementation.

## Documents

- [Architecture Overview](architecture-overview.md) - High-level system design
- [Detailed Architecture](architecture.md) - Component-level architecture

## Key Components

- **Provider Abstraction** - Pluggable compute providers (Mithril, local)
- **Task Engine** - Submission, monitoring, and lifecycle management
- **Data Layer** - Volume management and data mounting
- **Security Model** - Authentication and authorization

## Design Principles

1. Simple, obvious APIs
2. Explicit behavior over magic
3. Progressive disclosure of complexity
4. Clean abstractions without leakage