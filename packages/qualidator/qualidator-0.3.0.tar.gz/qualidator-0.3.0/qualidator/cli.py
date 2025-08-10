import click
import os
import json
from .inspectors.uniq import UniqInspector
from .inspectors.numeric import NumericInspector
from . import __version__
import shutil
from .connectors.databricks import DatabricksConnector
from .validations_registry import VALIDATIONS


CONFIG_FILE = "./.qualidations/config.json"
EXECUTIONS_RESULTS_FILE = "./.qualidations/execution_results.json"


@click.group()
@click.version_option(version=__version__, prog_name='qualidator', message='Qualidator CLI version: %(version)s')
def cli():
    """Qualidator CLI - manage data quality checks."""
    pass


@cli.command()
def init():
    """Initialize the Qualidations directory and set up a connector."""
    dir_path = './.qualidations'
    
    # Step 1: Create directory
    if os.path.exists(dir_path):
        click.secho(f"Directory '{dir_path}' already exists.", fg='yellow')
    else:
        try:
            os.mkdir(dir_path)
            click.secho("=" * 60, fg='cyan')
            click.secho("🎉 Welcome to QUALIDATOR! 🎉", fg='green', bold=True)
            click.secho("Your data quality journey begins here...", fg='blue')
            click.secho("-" * 60, fg='cyan')
            click.secho("📁 Directory '.qualidations' created successfully.", fg='green')
    
            providers = ["Databricks", "Snowflake", "Postgres", "None"]
            click.secho("\n🔌 Let's set up a data source connector.", fg='cyan')
            for idx, provider in enumerate(providers, start=1):
                click.echo(f"{idx}. {provider}")
            
            choice = click.prompt("Select a provider (enter number)", type=int)
            
            if choice < 1 or choice > len(providers):
                click.secho("❌ Invalid choice. Skipping connector setup.", fg='red')
                return
            
            selected_provider = providers[choice - 1]
            connector_config = {"provider": selected_provider}
            
            if selected_provider == "Databricks":
                connector_config["token"] = click.prompt("Enter your Databricks token", hide_input=True)
                connector_config["host"] = click.prompt("Enter your Databricks host URL")
                connector_config["warehouse_id"] = click.prompt("Enter your Databricks warehouse_id")
            
            elif selected_provider == "Snowflake":
                connector_config["account"] = click.prompt("Enter your Snowflake account")
                connector_config["username"] = click.prompt("Enter your Snowflake username")
                connector_config["password"] = click.prompt("Enter your Snowflake password", hide_input=True)
            
            elif selected_provider == "Postgres":
                connector_config["host"] = click.prompt("Enter Postgres host")
                connector_config["port"] = click.prompt("Enter Postgres port", default="5432")
                connector_config["user"] = click.prompt("Enter Postgres username")
                connector_config["password"] = click.prompt("Enter Postgres password", hide_input=True)
                connector_config["database"] = click.prompt("Enter Postgres database name")
            
            if selected_provider != "None":
                try:
                    with open(CONFIG_FILE, "w") as f:
                        json.dump(connector_config, f, indent=4)
                    click.secho(f"✅ Connector for {selected_provider} saved to {CONFIG_FILE}", fg='green')
                except Exception as e:
                    click.secho(f"❌ Failed to save connector config: {e}", fg='red')
            
            click.secho("🛠  You can now start adding validations with:", fg='blue')
            click.secho("    qualidator add --name is_not_null", fg='white')
            click.secho("    qualidator add --name column_values_are_unique", fg='white')
            click.secho("    qualidator add --name column_max_is_between", fg='white')
            click.secho("=" * 60, fg='cyan')

        except Exception as e:
            click.secho(f"❌ Failed to create directory: {e}", fg='red')
            return


@cli.command()
@click.option('--force', is_flag=True, help='Forcefully remove the Qualidations directory if it exists.')
def destroy(force):
    """Destroy the Qualidations directory."""
    dir_path = './.qualidations'
    
    if os.path.exists(dir_path):
        try:
            if force:
                shutil.rmtree(dir_path)
            else:
                os.rmdir(dir_path)
            click.secho("="*60, fg='red')
            click.secho("⚠ QUALIDATOR PROJECT DESTROYED ⚠", fg='red', bold=True)
            click.secho("The '.qualidations' directory has been removed.", fg='magenta')
            click.secho("We hope you enjoyed your stay. Come back soon!", fg='blue')
            click.secho("="*60, fg='red')
        except Exception as e:
            click.secho(f"❌ Failed to remove directory: {e}", fg='red')
    else:
        click.secho(f"Directory '{dir_path}' does not exist.", fg='yellow')


@cli.command(name='add')
@click.option('--name', required=True, help='Validation name to add.')
def add_validation(name):
    """Add validations to the suit."""

    validation = VALIDATIONS.get(name.lower())

    if not validation:
        click.secho(f"❗ Validation '{name}' is not supported yet.", fg='red')
        return

    table_name = click.prompt('Databricks: Please enter the table name in the format <CATALOG>.<SCHEMA>.<TABLE>', type=str, default='default_catalog.default_schema.default_table')
    
    # Prompt for parameters dynamically
    param_values = []
    for param_key, promt_text in validation['params']:
        val = click.prompt(promt_text, type=str)
        param_values.append(val)

    click.secho(validation['description'](*param_values), fg='green')

    # Build the query 
    if validation['inspector']:
        inspector = validation['inspector'](column_name=param_values[0], table_name=table_name)
        query = getattr(inspector, validation['method'])(*param_values[1:])
    else:
        query = validation['builder'](table_name, *param_values)

    # Save the query
    filename = f"./.qualidations/{table_name.replace('.', '_')}_{'_'.join(v.lower() for v in param_values)}_{name.lower()}.sql"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(query)

    click.secho(f"✔ Validation saved to {filename}", fg="green")


@cli.command(name='remove')
@click.option('--all', 'remove_all', is_flag=True, help='Remove all validations.')
@click.option('--name', help='Name of the validation to remove.')
def remove_validation(remove_all, name):
    """Remove validation(s) from the suite."""
    dir_path = './.qualidations'

    if not os.path.exists(dir_path):
        click.secho("❌ Validation directory does not exist. Run `qualidator init` first.", fg='yellow')
        return

    if remove_all:
        deleted = 0
        for file in os.listdir(dir_path):
            if file.endswith('.sql'):
                os.remove(os.path.join(dir_path, file))
                deleted += 1
        click.secho(f"🗑 Removed {deleted} validation(s).", fg='green')
        return

    if name:
        file_path = os.path.join(dir_path, f"{name}.sql")
        if os.path.exists(file_path):
            os.remove(file_path)
            click.secho(f"🗑 Removed validation '{name}'.", fg='green')
        else:
            click.secho(f"⚠ Validation '{name}' not found.", fg='yellow')
        return

    click.secho("❗ Please provide either --all or --name option.", fg='yellow')


@cli.command(name='status')
def show_validations():
    """Show validations project status."""
    dir_path = './.qualidations'

    if not os.path.exists(dir_path):
        click.secho("❗ No validations found.", fg='yellow')
        click.secho("👉 Run `qualidator init` to create the project.", fg='blue')
        return

    sql_files = [f for f in os.listdir(dir_path) if f.endswith('.sql')]

    if not sql_files:
        click.secho("📁 Project initialized, but no validations found.", fg='yellow')
        click.secho("✨ You can add one using:", fg='blue')
        click.secho("   qualidator add --name is_not_null", fg='white')
        return

    click.secho("="*60, fg='cyan')
    click.secho("📋 VALIDATIONS IN YOUR PROJECT", fg='green', bold=True)
    click.secho("-"*60, fg='cyan')

    for i, file in enumerate(sql_files, 1):
        base_name = file.replace('.sql', '')
        click.secho(f"{i}. {base_name}", fg='white')

    click.secho("-"*60, fg='cyan')
    click.secho(f"✅ Total: {len(sql_files)} validation(s) ready to go!", fg='green')
    click.secho("💡 You can remove with:", fg='blue')
    click.secho("   qualidator remove --name your_validation_name", fg='white')
    click.secho("="*60, fg='cyan')


@cli.command(name='run')
@click.option('--all', 'run_all', is_flag=True, help='Run all validations.')
@click.option('--name', help='Name of the validation to run.')
def run_validation(run_all, name):
    """Run validation(s) from the suite."""
    dir_path = './.qualidations'

    with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
        config = json.load(file)

    conn = DatabricksConnector(host=config.get('host'),
                               warehouse_id=config.get('warehouse_id'),
                               token=config.get('token'))

    if not os.path.exists(dir_path):
        click.secho("❗ No validations found. Run `qualidator init` first.", fg='yellow')
        return

    sql_files = [f for f in os.listdir(dir_path) if f.endswith('.sql')]

    if not sql_files:
        click.secho("📁 No validations to run. Add some with `qualidator add`.", fg='yellow')
        return

    if run_all:
        for file in sql_files:
            file_path = os.path.join(dir_path, file)
            click.secho(f"Running validation: {file}", fg='blue')

            with open(file_path, 'r', encoding='utf-8') as f:
                query = f.read()
            execution_result = conn.execute_query(query)

            with open(EXECUTIONS_RESULTS_FILE, 'a', encoding='utf-8') as results_file:
                json.dump({
                    "file": file,
                    "query": query,
                    "result": execution_result
                }, results_file, indent=4)

            if execution_result[0][-1]=='1':
                click.secho("✅ Validation passed.", fg='green')
            else:
                click.secho("❌ Validation failed.", fg='red')
            # click.secho(f"Execution result: {execution_result}", fg='green')
            
        click.secho("✅ All validations executed.", fg='green')
        return

    if name:
        file_name = f"{name}.sql"
        if file_name in sql_files:
            file_path = os.path.join(dir_path, file_name)
            click.secho(f"Running validation: {file_name}", fg='blue')
        
            with open(file_path, 'r', encoding='utf-8') as f:
                query = f.read()
            execution_result = conn.execute_query(query)
            # click.secho(f"Execution result: {execution_result}", fg='green')

            with open(EXECUTIONS_RESULTS_FILE, 'a', encoding='utf-8') as results_file:
                json.dump({
                    "file": file,
                    "query": query,
                    "result": execution_result
                }, results_file, indent=4)
    
            if execution_result[0][-1]=='1':
                click.secho("✅ Validation passed.", fg='green')
            else:
                click.secho("❌ Validation failed.", fg='red')
            
            click.secho("✅ Validation executed.", fg='green')
        else:
            click.secho(f"⚠ Validation '{name}' not found.", fg='yellow')
    else:
        click.secho("❗ Please provide either --all or --name option.", fg='yellow')





if __name__ == '__main__':
    cli()
