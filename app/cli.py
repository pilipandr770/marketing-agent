"""Apply manual migration for LinkedIn and Meta fields

This script can be run via Flask CLI:
    flask apply-manual-migration
"""
import os
from flask import Flask
from flask.cli import with_appcontext
import click
import psycopg


@click.command('apply-manual-migration')
@with_appcontext
def apply_manual_migration():
    """Apply manual SQL migration for LinkedIn and Meta fields"""
    
    # Get database URL from app config
    from flask import current_app
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not db_url:
        click.echo('❌ No database URL found in config')
        return
    
    # Read SQL file from project root (not app directory)
    project_root = os.path.dirname(os.path.dirname(__file__))
    sql_file = os.path.join(project_root, 'manual_migration.sql')
    
    if not os.path.exists(sql_file):
        click.echo(f'❌ SQL file not found: {sql_file}')
        click.echo(f'   Current directory: {os.getcwd()}')
        click.echo(f'   Project root: {project_root}')
        return
    
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Execute SQL
    try:
        conn = psycopg.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        
        # Verify columns were created
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'marketing_agent' 
            AND table_name = 'user'
            AND column_name IN ('linkedin_urn', 'meta_access_token', 'instagram_business_id')
            ORDER BY column_name
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        click.echo('✅ Manual migration applied successfully')
        click.echo(f'✅ Verified columns: {", ".join(columns)}')
        
    except Exception as e:
        click.echo(f'❌ Manual migration error: {e}')
        import traceback
        traceback.print_exc()


def init_app(app: Flask):
    """Register CLI command with Flask app"""
    app.cli.add_command(apply_manual_migration)
