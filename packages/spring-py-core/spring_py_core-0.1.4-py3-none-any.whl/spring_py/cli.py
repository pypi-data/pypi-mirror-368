"""
Spring-Py CLI - 项目生成工具
"""
import os
import argparse
import sys
from pathlib import Path
from typing import Dict, Any


class SpringPyCLI:
    """Spring-Py项目生成器"""
    
    def create_project(self, project_name: str, target_dir: str = None, template: str = "web"):
        """创建新项目"""
        if target_dir is None:
            target_dir = os.getcwd()
        
        project_path = Path(target_dir) / project_name
        
        if project_path.exists():
            print(f"❌ 错误: 目录 '{project_path}' 已存在")
            return False
        
        print(f"[INFO] 创建 Spring-Py 项目: {project_name}")
        print(f"[INFO] 目标目录: {project_path}")
        
        try:
            # 创建项目目录结构
            self._create_directory_structure(project_path)
            
            # 生成项目文件
            self._generate_project_files(project_path, project_name)
            
            print(f"✅ 项目创建成功!")
            print(f"\n📋 下一步:")
            print(f"   cd {project_name}")
            print(f"   pip install -e .  # 或 uv sync")
            print(f"   python src/main/application.py")
            print(f"\n🌐 应用将在 http://localhost:8000 启动")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建项目失败: {e}")
            # 清理失败的目录
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path)
            return False
    
    def _create_directory_structure(self, project_path: Path):
        """创建目录结构"""
        print(f"📁 创建目录结构...")
        
        directories = [
            "src/main",
            "src/main/controller",
            "src/main/service", 
            "src/main/model",
            "src/main/param",
            "src/test"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
        
        print(f"✓ 目录结构创建完成")
    
    def _generate_project_files(self, project_path: Path, project_name: str):
        """生成项目文件"""
        print(f"📝 生成项目文件...")
        
        # 生成 pyproject.toml
        self._generate_pyproject_toml(project_path, project_name)
        
        # 生成主应用文件
        self._generate_application_py(project_path, project_name)
        
        # 生成 README.md
        self._generate_readme(project_path, project_name)
        
        # 生成配置文件
        self._generate_config_files(project_path, project_name)
        
        # 生成示例服务和控制器
        self._generate_example_files(project_path)
        
        print(f"✓ 项目文件生成完成")
    
    def _generate_pyproject_toml(self, project_path: Path, project_name: str):
        """生成 pyproject.toml"""
        content = f'''[project]
name = "{project_name}"
version = "0.1.2"
description = "A Spring-Py based web application"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "spring-py-core>=0.1.1/",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
keywords = ["spring", "fastapi", "web", "framework"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[project.scripts]
{project_name} = "main.application:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.pytest.ini_options]
testpaths = ["src/test"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "I", "N", "W"]
'''
        (project_path / "pyproject.toml").write_text(content, encoding='utf-8')
    
    def _generate_application_py(self, project_path: Path, project_name: str):
        """生成应用主文件"""
        content = f'''"""
{project_name.title().replace("-", " ")} - Spring-Py Web应用程序
"""
"""
Myapp - Spring-Py Web应用程序
"""
from spring_py import SpringBootApplication, Component, Autowired, get_bean, RestController, Service
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import uvicorn
import os


@Service
class UserService:
    """用户服务示例"""
    
    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
        }
        print("📋 UserService 初始化完成")
    
    def get_user(self, user_id: int):
        """获取用户信息"""
        return self.users.get(user_id)
    
    def get_all_users(self):
        """获取所有用户"""
        return list(self.users.values())
    
    def create_user(self, name: str, email: str):
        """创建新用户"""
        user_id = max(self.users.keys()) + 1 if self.users else 1
        user = {"id": user_id, "name": name, "email": email}
        self.users[user_id] = user
        return user


@Service
class HealthService:
    """健康检查服务"""
    
    def get_health_status(self):
        """获取应用健康状态"""
        return {
            "status": "healthy",
            "service": "myapp",
            "version": "0.1.0",
            "framework": "Spring-Py + FastAPI"
        }


@RestController
class UserController:
    """用户控制器"""
    
    user_service: UserService = Autowired()
    
    def setup_routes(self) -> APIRouter:
        """设置用户相关路由"""
        router = APIRouter(prefix="/api/users", tags=["Users"])
        
        @router.get("/")
        async def get_users():
            """获取所有用户"""
            users = self.user_service.get_all_users()
            return {"users": users, "total": len(users)}
        
        @router.get("/{user_id}")
        async def get_user(user_id: int):
            """根据ID获取用户"""
            user = self.user_service.get_user(user_id)
            if user:
                return user
            return JSONResponse(
                status_code=404,
                content={"error": "User not found"}
            )
        
        @router.post("/")
        async def create_user(name: str, email: str):
            """创建新用户"""
            user = self.user_service.create_user(name, email)
            return JSONResponse(
                status_code=201,
                content=user
            )
        
        return router


@RestController
class HealthController:
    """健康检查控制器"""
    
    health_service: HealthService = Autowired()
    
    def setup_routes(self) -> APIRouter:
        """设置健康检查路由"""
        router = APIRouter(tags=["Health"])
        
        @router.get("/health")
        async def health_check():
            """健康检查端点"""
            return self.health_service.get_health_status()
        
        @router.get("/")
        async def root():
            """根路径"""
            return {
                "message": "Welcome to Myapp API",
                "version": "0.1.0",
                "framework": "Spring-Py + FastAPI",
                "docs": "/docs",
                "health": "/health"
            }
        
        return router


@SpringBootApplication()
class Application:
    """Spring Boot风格的应用程序主类"""
    
    def create_app(self) -> FastAPI:
        """创建FastAPI应用实例"""
        app = FastAPI(
            title="Myapp API",
            description="A Spring-Py based web application",
            version="0.1.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 注册路由
        user_controller = get_bean(UserController)
        health_controller = get_bean(HealthController)
        
        app.include_router(user_controller.setup_routes())
        app.include_router(health_controller.setup_routes())
        
        return app


def main():
    """应用程序主入口"""
    print("🚀 启动 Myapp 应用...")
    
    # 启动Spring-Py应用上下文
    app = Application()
    context = app.run()
    
    # 创建FastAPI实例
    fastapi_app = app.create_app()
    
    print("✅ 应用启动成功!")
    print("📖 API文档: http://localhost:8000/docs")
    print("🏥 健康检查: http://localhost:8000/health")
    print("🌐 应用地址: http://localhost:8000")
    
    # 启动Web服务器
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENV") == "dev" else False
    )


if __name__ == "__main__":
    main()
'''
        (project_path / "src" / "main" / "application.py").write_text(content, encoding='utf-8')
    
    def _generate_readme(self, project_path: Path, project_name: str):
        """生成 README.md"""
        title = project_name.title().replace("-", " ")
        content = f'''# {title}

一个基于Spring-Py框架的现代化Web应用程序。

## 特性

- 🚀 **Spring-Py框架** - 类似Spring Boot的Python依赖注入框架
- 🌐 **FastAPI集成** - 高性能异步Web框架
- 📁 **标准项目结构** - 清晰的分层架构
- 🔧 **依赖注入** - 自动化的组件管理
- 📝 **类型注解** - 完整的类型提示支持

## 项目结构

```
{project_name}/
├── src/
│   ├── main/
│   │   ├── application.py      # 应用程序主入口
│   │   ├── controller/         # 控制器层
│   │   ├── service/           # 服务层
│   │   ├── model/             # 数据模型
│   │   └── param/             # 参数定义
│   └── test/                  # 测试代码
├── pyproject.toml            # 项目配置
└── README.md                 # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
# 使用pip
pip install -e .

# 或使用uv（推荐）
uv sync
```

### 2. 运行应用

```bash
python src/main/application.py
```

### 3. 访问应用

- **应用首页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## API接口

### 用户管理

- `GET /api/users/` - 获取所有用户
- `GET /api/users/{{user_id}}` - 根据ID获取用户
- `POST /api/users/` - 创建新用户

### 系统

- `GET /health` - 健康检查
- `GET /` - 应用信息

## 开发指南

### 创建服务

```python
from spring_py import Component

@Component
class MyService:
    def do_something(self):
        return "Hello from MyService"
```

### 创建控制器

```python
from spring_py import Component, Autowired
from fastapi import APIRouter

@Component
class MyController:
    my_service: MyService = Autowired()
    
    def setup_routes(self) -> APIRouter:
        router = APIRouter(prefix="/api/my")
        
        @router.get("/")
        async def my_endpoint():
            return self.my_service.do_something()
        
        return router
```

## 测试

```bash
# 运行测试
pytest src/test/

# 查看测试覆盖率
pytest --cov=main --cov-report=html src/test/
```

## 部署

### 生产环境运行

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main.application:app
```

### Docker部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["python", "src/main/application.py"]
```

## 许可证

MIT License
'''
        (project_path / "README.md").write_text(content, encoding='utf-8')
    
    def _generate_config_files(self, project_path: Path, project_name: str):
        """生成配置文件"""
        # .gitignore
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Environment variables
.env.local
.env.development
.env.production
'''
        (project_path / ".gitignore").write_text(gitignore_content, encoding='utf-8')
        
        # .env.example
        env_content = f'''# {project_name.title()} Environment Variables

# Application
APP_NAME={project_name}
APP_VERSION=0.1.0
ENV=dev

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Database (if needed)
# DATABASE_URL=sqlite:///./app.db

# Logging
LOG_LEVEL=INFO
'''
        (project_path / ".env.example").write_text(env_content, encoding='utf-8')
    
    def _generate_example_files(self, project_path: Path):
        """生成示例文件"""
        # __init__.py 文件
        init_files = [
            "src/__init__.py",
            "src/main/__init__.py",
            "src/main/controller/__init__.py",
            "src/main/service/__init__.py",
            "src/main/model/__init__.py",
            "src/main/param/__init__.py",
            "src/test/__init__.py"
        ]
        
        for init_file in init_files:
            (project_path / init_file).write_text('# Package initialization\n', encoding='utf-8')
        
        # 示例测试文件
        test_content = '''"""
应用程序测试示例
"""
import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main.application import Application, UserService, HealthService

def test_user_service():
    """测试用户服务"""
    service = UserService()
    
    # 测试获取用户
    user = service.get_user(1)
    assert user is not None
    assert user["name"] == "Alice"
    
    # 测试创建用户
    new_user = service.create_user("Charlie", "charlie@example.com")
    assert new_user["name"] == "Charlie"
    assert new_user["email"] == "charlie@example.com"

def test_health_service():
    """测试健康检查服务"""
    service = HealthService()
    status = service.get_health_status()
    
    assert status["status"] == "healthy"
    assert "version" in status

def test_application_context():
    """测试Spring-Py应用上下文"""
    app = Application()
    context = app.run()
    
    # 检查组件是否正确注册
    components = context.list_components()
    component_names = [c.__name__ for c in components]
    
    assert "UserService" in component_names
    assert "HealthService" in component_names
    assert "UserController" in component_names
    assert "HealthController" in component_names

if __name__ == "__main__":
    pytest.main([__file__])
'''
        (project_path / "src" / "test" / "test_application.py").write_text(test_content, encoding='utf-8')
    
    def list_templates(self):
        """列出可用模板"""
        templates = {
            "web": "Web API应用 (FastAPI + Spring-Py)",
            "cli": "命令行工具",
            "worker": "后台任务工具"
        }
        
        print("📋 可用模板:")
        for name, desc in templates.items():
            print(f"  {name:<10} - {desc}")


def main():
    """CLI主入口"""
    parser = argparse.ArgumentParser(
        description="Spring-Py 项目生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  spring-py create my-web-app              # 创建Web应用
  spring-py create my-api --template web   # 指定模板创建
  spring-py templates                      # 列出可用模板
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("name", help="项目名称")
    create_parser.add_argument("--template", "-t", default="web", help="模板类型 (默认: web)")
    create_parser.add_argument("--dir", "-d", help="目标目录 (默认: 当前目录)")
    
    # templates 命令
    subparsers.add_parser("templates", help="列出可用模板")
    
    # version 命令
    subparsers.add_parser("version", help="显示版本信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SpringPyCLI()
    
    if args.command == "create":
        success = cli.create_project(args.name, args.dir, args.template)
        sys.exit(0 if success else 1)
    
    elif args.command == "templates":
        cli.list_templates()
    
    elif args.command == "version":
        print("Spring-Py CLI v0.1.0")
        print("基于 Spring-Py 框架的项目生成工具")


if __name__ == "__main__":
    main()
