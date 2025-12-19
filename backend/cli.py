import click
import os
from dotenv import load_dotenv
from backend.agents.graph_agent import MovieAgentSystem

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

@click.command()
@click.option('--query', '-q', help='Query to ask')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def cli(query, interactive):
    """CLI interface for the movie agent system"""
    agent = MovieAgentSystem()
    
    if interactive:
        click.echo(" Movie Agent CLI (type 'exit' to quit)")
        while True:
            user_input = click.prompt('\nYou', type=str)
            if user_input.lower() in ['exit', 'quit']:
                break
            
            try:
                result = agent.run(user_input)
                click.echo(f"\n Agent: {result.get('answer', 'No answer generated.')}")
            except Exception as e:
                click.echo(f" Error: {e}")
    
    elif query:
        try:
            result = agent.run(query)
            click.echo(result.get('answer', 'No answer generated.'))
        except Exception as e:
            click.echo(f" Error: {e}")
    
    else:
        click.echo("Please provide --query or use --interactive")

if __name__ == '__main__':
    cli()
