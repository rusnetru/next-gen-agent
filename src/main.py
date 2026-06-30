import os

from dotenv import load_dotenv

from src.agent.end_to_end import EndToEndAgent


def main() -> None:
    load_dotenv()
    use_llm = bool(os.environ.get("DEEPSEEK_API_KEY"))

    agent = EndToEndAgent(use_llm=use_llm)
    result = agent.run("research the competitor landscape and execute a summary report")

    print(f"task: {result.task}")
    print(f"strategy: {result.strategy} (attempts: {result.attempts})")
    print(f"succeeded: {result.succeeded}")
    for line in result.orchestration["transcript"]:
        print(f"  {line}")


if __name__ == "__main__":
    main()
