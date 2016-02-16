import logging, os, thread, logging.config
import datetime as dt

__prefix__ = 'aq'
__pid__ = os.getpid()
__loggers__ = []
class py_formatter(logging.Formatter):

    converter = dt.datetime.fromtimestamp
    def formatTime(self, record, dateFmt=None):
        ct = self.converter(record.created)
        s = ct.strftime(dateFmt) if dateFmt else ct.strftime("%Y-%m-%d %H:%M:%S")
        s += ",%03d [%d-%d]" % (record.msecs, __pid__, thread.get_ident())
        return s

class py_logging(object):

    @staticmethod
    def getLogger(name = None):
        if name is None:
            return logging.getLogger(__prefix__)
        if name.startswith(__prefix__):
            return logging.getLogger(__prefix__)
        logger = logging.getLogger(__prefix__ + '.' + name)
        __loggers__.append(logger)
        return logger

    @staticmethod
    def configure(logFilename = None, logFilemode='a', logFileLevel = logging.INFO,
        logToConsole=True, logToConsoleLevel = logging.DEBUG ):

        verboseFormat = '%(asctime)s [%(process)d-%(thread)d] %(levelname)s %(name)s : %(message)s'
        simpleFormat='%(levelname)s %(message)s'

        logConfig = {
            'version':1,
            'formatters': {
                'simple': { 'format':simpleFormat, },
                'verbose': { 'format':verboseFormat, }
            },
            'handlers':{
                'console':{
                    'class':'logging.StreamHandler', 'formatter':'verbose', 'level':logToConsoleLevel
                },
            },
            'loggers':{
                #'':{'handlers':['console'], 'propagate': False, 'level':logging.DEBUG},
                __prefix__:{'handlers':['console'], 'qualname':__prefix__, 'propagate':True, 'level':logging.DEBUG},
            },
            #'root':{'handlers':('console', 'file'), 'level':logging.DEBUG},
        }

        if logFilename is not None:
            logConfig['handlers']['file'] = {
                'class':'logging.FileHandler', 'filename':logFilename, 'mode': logFilemode,
                'formatter':'verbose', 'level':logFileLevel
            }
            #logConfig['handlers']['file'] = {
            #    'class':'logging.handlers.RotatingFileHandler', 'filename':logFilename,
            #    'formatter':'verbose', 'level':logFileLevel, 'maxBytes' : 1024, 'backupCount' : 3,
            #}
            for key, handle in logConfig['loggers'].items():
                handle['handlers'].append('file')

        logging.config.dictConfig(logConfig)

    @staticmethod
    def shutdown():
        logging.shutdown()



