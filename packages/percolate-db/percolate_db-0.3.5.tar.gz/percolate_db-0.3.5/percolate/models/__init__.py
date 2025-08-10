from pydantic import Field, BaseModel
from functools import partial
import typing

     

def EmbeddedField(embedding_provider='default')->Field:
    return partial(Field, json_schema_extra={'embedding_provider':embedding_provider})

DefaultEmbeddingField = EmbeddedField()

def KeyField():
    return partial(Field, json_schema_extra={'is_key':True})

KeyField = KeyField()

from . import utils
from .MessageStack import  MessageStack
from .AbstractModel import AbstractModel
from . import media

def get_p8_models():
    """convenience to load all p8 models in the library"""
    
    from percolate.models.inspection import get_classes
    return get_classes(package="percolate.models.p8")


from .p8 import *
from .p8.types import UserMemory 


"""For now we whitelist the models that are installed in the database"""
CORE_INSTALL_MODELS= [ User, Project, Agent, ModelField, LanguageModelApi, Function, Session, SessionEvaluation, AIResponse, ApiProxy, PlanModel,
               Settings, PercolateAgent, IndexAudit, Task, TaskResources, ResearchIteration , Resources,SessionResources, Schedule, Audit, UserMemory]
   
def migrate_core_models():
    """apply schema changes"""
    
    results = []
    for model in CORE_INSTALL_MODELS:
        print(f"""***{model}***""")
        results.append( p8.repository(model).register() )
    """TODO results are not ready yet - but we should display a report - in the CLI debug messages will now be shown and we want a table"""
        
    """make this a polars dataframe for display"""
    return results
   
def repository(model:BaseModel, **kwargs):
    """Repository factory function.
    
    First tries to use PostgresService, then falls back to DuckDBService
    if embedded services are available.
    
    Args:
        model: Pydantic model to create repository for
        **kwargs: Additional arguments for service initialization
    
    Returns:
        Repository instance
    """
    try:
        from percolate.services import PostgresService
        return PostgresService(model, **kwargs)
    except ImportError:
        try:
            from percolate.services.embedded import DuckDBService
            return DuckDBService(model, **kwargs)
        except ImportError:
            raise ImportError("No database service available. Install either psycopg2-binary or duckdb.")

def bootstrap(apply:bool = False, apply_to_test_database: bool= True, root='../../../../extension/', alt_connection:str=None):
    """util to generate the sql that we use to setup percolate"""

    from percolate.models.p8 import sample_models
    from percolate.models.utils import SqlModelHelper
    from percolate.services import PostgresService
    from percolate.utils.env import TESTDB_CONNECTION_STRING
    from percolate.models.p8.native_functions import get_native_functions
    import glob
    
    pg = PostgresService(on_connect_error='ignore')
    
    if alt_connection:
        pg = PostgresService(connection_string=alt_connection)
    elif apply_to_test_database:
        print('Using test database and will create it if it does not exist')
        apply = True
        pg._create_db('test')
        pg = PostgresService(connection_string=TESTDB_CONNECTION_STRING)
    
        
    root = root.rstrip('/')
    print('********Building queries*******')
    """build a list of models we want to init with"""
    
    models = CORE_INSTALL_MODELS
    
    """compile the functions into one file"""
    with open(f'{root}/sql/01_add_functions.sql', 'w') as f:
        print(f)
        for sql in glob.glob(f'{root}/sql-staging/p8_pg_functions/**/*.sql',recursive=True):
            print(sql)
            with open(sql, 'r') as sql:
                f.write(sql.read())
                f.write('\n\n---------\n\n')

    """add base tables"""            
    with open(f'{root}/sql/02_create_primary.sql', 'w') as f:
        print(f)
        for model in models:
            f.write(pg.repository(model,on_connect_error='ignore').model_registration_script(secondary=False, primary=True))

    """add the rest"""
    with open(f'{root}/sql/03_create_secondary.sql', 'w') as f:    
        print(f)
        for model in models:
            print(model)
            f.write(pg.repository(model,on_connect_error='ignore').model_registration_script(secondary=True, primary=False))
            
        script = SqlModelHelper(LanguageModelApi).get_data_load_statement(sample_models)
        f.write('\n\n-- -----------\n')
        f.write('-- sample models--\n\n')
        f.write(script)
        
        """add native functions"""
        script = SqlModelHelper(Function).get_data_load_statement(get_native_functions())
        f.write('\n\n-- -----------\n')
        f.write('-- native functions--\n\n')
        f.write(script)
        
    if apply:
        _test_apply(root=root, pg=pg)
        
def _test_apply(root='../../../../extension/', pg = None):
    """
    these are utility test methods - but we will add them to an automated deployment test script later
    passing the database in e.g. in test mode - we will clean this up later
    """
    
    from percolate.services import PostgresService
    pg = pg or PostgresService()

    print('*****applying sql schema...******')
    print()
    root = root.rstrip('/')
   
    with open(f"{root}/sql/00_install.sql") as f:
        sql = f.read()
        pg.execute(sql)
        
    with open(f"{root}/sql/01_add_functions.sql") as f:
        sql = f.read()
        pg.execute(sql)

    with open(f"{root}/sql/02_create_primary.sql") as f:
        sql = f.read()
        pg.execute(sql)
    with open(f"{root}/sql/03_create_secondary.sql") as f:
        sql = f.read()
        pg.execute(sql)
        
    with open(f"{root}/sql/10_finalize.sql") as f:
        sql = f.read()
        pg.execute(sql)
        
    print('********done*******')