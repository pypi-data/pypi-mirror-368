# Gobe Framework

**Modern Python Web Framework with Unity Integration**

Gobe is a next-generation web framework designed to bridge the gap between web development and game development. Built with modern Python practices, it provides a familiar Django-like experience while preparing for seamless Unity integration.

## ✨ Features

### 🚀 **Modern Web Development**
- **Intuitive CLI** - Project scaffolding and management
- **Auto-routing** - Convention-based URL routing
- **Hybrid Templates** - Django + JSX-style templating
- **Powerful ORM** - Type-safe database operations
- **Built-in APIs** - REST, GraphQL, and WebSocket support

### 🎮 **Game-Ready Architecture**
- **Unity Bridge** - Future-ready game engine integration
- **Real-time Communication** - WebSocket for live gameplay
- **Game Modules** - Specialized components for game logic
- **Scalable Backend** - Built for multiplayer games

### 🛠 **Developer Experience**
- **Hot Reload** - Instant development feedback
- **Auto-migrations** - Intelligent database schema updates
- **Rich CLI** - Comprehensive command-line tools
- **Plugin System** - Extensible architecture

## 🚀 Quick Start

### Installation

```bash
pip install gobe-framework
```

### Create Your First Project

```bash
# Create a new Gobe project
gobe create-project my_game_backend

# Navigate to project
cd my_game_backend

# Start development server
gobe serve
```

Your Gobe application is now running at `http://localhost:8000`!

## 📁 Project Structure

```
my_game_backend/
├── gobe_config/          # Configuration files
│   └── settings.py
├── web_apps/             # Web applications
│   └── main/
│       ├── __init__.py
│       ├── models.py     # Database models
│       ├── views.py      # Request handlers
│       └── api_views.py  # API endpoints
├── game_modules/         # Game-specific modules (future)
├── shared/               # Shared code
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── api/                  # API configuration
└── main.py              # Application entry point
```

## 🔧 Core Concepts

### Models (ORM)

Define your data models with a clean, type-safe API:

```python
from gobe.database.orm import Model
from gobe.database.orm.fields import CharField, IntegerField, DateTimeField

class Player(Model):
    username = CharField(max_length=50, unique=True)
    score = IntegerField(default=0)
    level = IntegerField(default=1)
    created_at = DateTimeField(auto_now_add=True)

# Query your data
players = Player.objects.filter(level__gt=5).order_by('-score')
top_player = Player.objects.get(username='champion')
```

### Views

Handle requests with class-based or function-based views:

```python
from gobe.web.views import View
from gobe.web.routing import get, post

class LeaderboardView(View):
    template_name = 'leaderboard.html'
    
    def get(self, request):
        players = Player.objects.order_by('-score')[:10]
        return self.render(request, {'players': players})

# Or use decorators
@get('/api/players/')
def get_players(request):
    players = Player.objects.all()
    return JsonResponse([p.to_dict() for p in players])
```

### API Development

Build REST APIs effortlessly:

```python
from gobe.api.rest import ModelViewSet
from gobe.api.rest.permissions import IsAuthenticated

class PlayerViewSet(ModelViewSet):
    model = Player
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Player.objects.filter(user=self.request.user)
```

### Templates

Use familiar template syntax with modern features:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    
    {% if players %}
        <ul>
        {% for player in players %}
            <li>{{ player.username }} - Level {{ player.level }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No players found.</p>
    {% endif %}
</body>
</html>
```

## 🌐 API Support

### REST API

```python
# Automatic CRUD endpoints
class GameSessionViewSet(ModelViewSet):
    model = GameSession
    serializer_class = GameSessionSerializer
    
    # GET /api/gamesessions/
    # POST /api/gamesessions/
    # GET /api/gamesessions/{id}/
    # PUT /api/gamesessions/{id}/
    # DELETE /api/gamesessions/{id}/
```

### GraphQL (Coming Soon)

```python
from gobe.api.graphql import ObjectType, Field, GraphQLSchema

class PlayerType(ObjectType):
    username = Field(String)
    score = Field(Int)
    level = Field(Int)

class Query(ObjectType):
    players = Field(List(PlayerType))
    
    def resolve_players(self, info):
        return Player.objects.all()

schema = GraphQLSchema(query=Query)
```

### WebSocket

```python
from gobe.api.websocket import WebSocketHandler

class GameHandler(WebSocketHandler):
    async def on_connect(self, connection):
        await connection.send({'type': 'welcome'})
    
    async def on_message(self, connection, data):
        # Handle real-time game events
        await self.broadcast_to_room(data['room'], {
            'type': 'game_update',
            'data': data
        })
```

## 🎯 CLI Commands

Gobe provides a comprehensive CLI for project management:

```bash
# Project creation
gobe create-project <name> [--template=basic|api|fullstack]

# App management
gobe add-app <name> [--type=web|api|game]

# Development
gobe serve [--host=127.0.0.1] [--port=8000] [--reload]

# Database operations
gobe migrate [--auto] [--dry-run]

# Production
gobe build [--optimize] [--output=dist]
gobe deploy [--target=docker|heroku|aws]
```

## 🎮 Unity Integration (Coming Soon)

Gobe is designed with future Unity integration in mind:

```python
# Game module example
from gobe.unity_bridge import UnityBridge
from gobe.game_modules import GameModule

class MyGameModule(GameModule):
    def setup(self, app):
        # Register Unity message handlers
        self.bridge = UnityBridge()
        self.bridge.on('player_move', self.handle_player_move)
    
    async def handle_player_move(self, data):
        # Process Unity game events
        player = await Player.objects.aget(id=data['player_id'])
        player.position = data['position']
        await player.asave()
```

## 📖 Documentation

- **[Getting Started Guide](https://gobe.dev/docs/getting-started)**
- **[API Reference](https://gobe.dev/docs/api)**
- **[Tutorials](https://gobe.dev/docs/tutorials)**
- **[Unity Integration](https://gobe.dev/docs/unity)** (Coming Soon)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Roadmap

### Phase 1: Core Framework ✅
- [x] CLI system
- [x] Project scaffolding
- [x] ORM and database layer
- [x] Web views and routing
- [x] Template engine
- [x] REST API support

### Phase 2: Enhanced APIs
- [ ] GraphQL implementation
- [ ] WebSocket optimization
- [ ] Real-time subscriptions
- [ ] Advanced caching

### Phase 3: Unity Bridge
- [ ] Unity C# bridge library
- [ ] Real-time game state sync
- [ ] Asset management integration
- [ ] Multiplayer game templates

### Phase 4: Production Ready
- [ ] Performance optimizations
- [ ] Monitoring and analytics
- [ ] Cloud deployment tools
- [ ] Enterprise features

## 💡 Examples

Check out our example projects:

- **[Blog Application](examples/blog)** - Traditional web development
- **[REST API](examples/api)** - Pure API backend
- **[Game Backend](examples/game)** - Multiplayer game server (Coming Soon)

## 🙋‍♂️ Support

- **[Discord Community](https://discord.gg/gobe)**
- **[GitHub Issues](https://github.com/gobe-team/gobe-framework/issues)**
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/gobe-framework)**

---

**Built with ❤️ by the Gobe Team**

*Bridging Web and Game Development*
