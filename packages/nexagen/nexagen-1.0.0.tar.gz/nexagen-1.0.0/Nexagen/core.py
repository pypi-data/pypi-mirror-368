import json
import subprocess
import asyncio
import os
import sys
import traceback
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from .utils import (
    call_llm,
    generate_agent_card
)
import time
from .prompt import generate_agent_cards_prompt

# 模板环境设置
TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def create_project(project_path: Path):
    """Create new project structure"""
    project_path.mkdir(exist_ok=True)
    (project_path / "__init__.py").touch()
    (project_path / "mcp_agents").mkdir(exist_ok=True)
    (project_path / "mcp.json").write_text(json.dumps({}), encoding='utf-8')
    env_data=open(f"{Path(__file__).parent}/.env","r",encoding="utf-8").read()
    (project_path / ".env").write_text(env_data, encoding='utf-8')


def build_project(project_path: Path):
    """Build the Nexagen system"""
    try:
        print("Starting Nexagen system build...")
        load_dotenv(project_path / ".env")

        # 1. 安装依赖
        print("Installing dependencies...")
        subprocess.run(["uv", "pip", "install", "a2a-sdk", "mcp", "uvicorn", "httpx", "jinja2", "python-dotenv"])

        try:
            #生成auto_find_mcp_agents
            try:
                print("Generating agent executor...")
                executor_template = env.get_template("auto_find_mcp_agents.py.j2")
                rendered_content = executor_template.render()
                (project_path / "auto_find_mcp_agents.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering auto_find_mcp_agents template: {e}")
                #traceback.print_exc()
                #raise
            #执行auto_find_mcp_agents
            os.system("python auto_find_mcp_agents.py")
            os.remove("auto_find_mcp_agents.py")
            # 2. 生成智能体卡片
            print("Generating agent cards...")

            (project_path / "agent_cards").mkdir(exist_ok=True)
            agent_cards = []

            # 读取 mcp_cards
            with open(f"{project_path}/mcp_agents/mcp_cards.json", encoding="utf-8") as fh:
                mcp_data = fh.read()

            #print("mcp_data")
            #print(mcp_data)

            prompt = f"{generate_agent_cards_prompt}\n{mcp_data}"
            agents = call_llm(prompt)
            agents_list = json.loads(agents.replace("```json", "").replace("```", ""))

            for agent_file in agents_list:
                print(f"Processing agent: {agent_file['name']}")
                card = generate_agent_card(
                    name=agent_file["name"],
                    description=agent_file["description"],
                    tools=agent_file["skills"],
                    url=agent_file["url"],
                    capabilities=agent_file["capabilities"],
                    default_input_modes=agent_file["defaultInputModes"],
                    default_output_modes=agent_file["defaultOutputModes"]
                )

                card_path = project_path / "agent_cards" / f"{agent_file['name']}.json"
                card_path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding='utf-8')
                agent_cards.append(str(card_path.relative_to(project_path)))
            print("Build agent cards ok.")
            # 3. 生成调度Agent
            try:
                print("Generating orchestrator agent...")

                #orchestrator_template = env.get_template("orchestrator_agent.py.j2")
                #rendered_content = orchestrator_template.render()
                (project_path / "orchestrator_agent.py").write_text((TEMPLATES_DIR/"orchestrator_agent.py.j2").read_text(encoding='utf-8'), encoding='utf-8')
            except Exception as e:
                print(f"Error rendering orchestrator template: {e}")
                #traceback.print_exc()
                #raise

            # 4. 生成MCP客户端
            try:
                print("Generating MCP client...")
                mcp_client_template = env.get_template("mcp_client.py.j2")
                rendered_content = mcp_client_template.render()
                (project_path / "mcp_client.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering MCP client template: {e}")
                #traceback.print_exc()
                #raise

            # 5. 生成Agent执行器
            try:
                print("Generating agent executor...")
                executor_template = env.get_template("agent_executor.py.j2")
                rendered_content = executor_template.render()
                (project_path / "agent_executor.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering agent executor template: {e}")
                #traceback.print_exc()
                #raise
            #print()
            # 6. 生成Agent pipeline
            try:
                print("Generating Agent pipeline...")
                pipeline_template = env.get_template("pipeline.py.j2")
                rendered_content = pipeline_template.render()
                (project_path / "pipeline.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering pipeline template: {e}")
                # traceback.print_exc()
                # raise
            #print()
            # 7. 生成Demo
            try:
                print("Generating Agent Demo...")
                test_demo_template = env.get_template("test_demo.py.j2")
                rendered_content = test_demo_template.render()
                (project_path / "test_demo.py").write_text(rendered_content, encoding='utf-8')
            except Exception as e:
                print(f"Error rendering test_demo template: {e}")
                # traceback.print_exc()
                # raise

        except Exception as err:
            print(err)

    except Exception as e:
        print(f"Build failed: {e}")
        #traceback.print_exc()
        #sys.exit(1)


def run_project(project_path: Path):
    """Run the Nexagen system"""
    try:
        print("Starting Nexagen system...")
        try:
            # 1. 运行A2A客户端
            print("Starting Nexagen client...")
            os.system("python test_demo.py")
        except Exception as err:
            print(err)

    except Exception as e:
        print(f"Run failed: {e}")
        #traceback.print_exc()
        #sys.exit(1)