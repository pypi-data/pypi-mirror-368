from whatap.trace import get_dict
from whatap.trace.mod.application.wsgi import (
    trace_handler,
    interceptor_db_con,
    interceptor_db_execute,
    interceptor_db_close
)
db_info = {}

def get_db_info(session):
    db_info = {'type' : 'neo4j'}

    pool = getattr(session, '_pool', None)

    host = None
    port = None
    user = None
    db_name = None

    try:
        if pool:
            addr = getattr(pool, 'address', getattr(pool, '_address', None))
            if addr:
                host, port = addr[0], addr[1]
    except Exception:
        pass
    db_info["host"] = f"{host}:{port}"

    try:
        if pool:
            auth_token = pool.get_auth()
            if auth_token:
                user = getattr(auth_token, 'principal', None)
    except Exception as e:
        pass

    if user == None:
        db_info["user"] = "neo4j"
    else:
        db_info["user"] = user

    try:
        session_config = getattr(session, '_config', None)
        if session_config:
            db_name = getattr(session_config, 'database', None)
    except Exception:
        pass

    if db_name == None:
        db_info["dbname"] = "default"
    else:
        db_info["dbname"] = db_name



    return db_info




def instrument_neo4j(module):
    orig = module.Session.run

    def wrapper(fn):
        @trace_handler(fn)
        def trace(session, *args, **kwargs):
            db_info = get_db_info(session)
            try:
                setattr(session, 'rowcount', -1)
            except Exception as e:
                raise e
            callback = interceptor_db_execute(fn, db_info, session, *args, **kwargs)

            return callback
        return trace

    module.Session.run = wrapper(orig)




    orig = module.Session.close

    def wrapper(fn):
        @trace_handler(fn)
        def trace(session, *args, **kwargs):
            callback = interceptor_db_close(fn, session ,*args, **kwargs)
            return callback
        return trace

    module.Session.close = wrapper(orig)





    def wrapper(fn):
        @trace_handler(fn)
        def trace(tx, *args, **kwargs):
            session = None
            try:
                session = tx._on_closed.__self__
            except AttributeError:
                return fn(tx, *args, **kwargs)

            db_info = get_db_info(session)
            try:
                setattr(tx, 'rowcount', -1)
            except Exception:
                pass
            callback = interceptor_db_execute(fn, db_info, tx, *args, **kwargs)
            return callback

        return trace

    tx_classes_to_patch = ['Transaction', 'ManagedTransaction', 'BoltTransaction']

    for class_name in tx_classes_to_patch:
        if hasattr(module, class_name):
            TxClass = getattr(module, class_name)
            if hasattr(TxClass, 'run'):
                original_run = getattr(TxClass, 'run')
                setattr(TxClass, 'run', wrapper(original_run))



