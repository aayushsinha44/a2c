import logging

class Log():

    logging.basicConfig(filename='file.log', 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 

    _logger=logging.getLogger()

    _logger.setLevel(logging.DEBUG)

    @staticmethod
    def log(message, level='info'):

        if level=='debug':
            Log._logger.debug(message) 
        elif level=='info':
            Log._logger.info(message) 
        elif level=='warning':
            Log._logger.warning(message)
        elif level=="error": 
            Log._logger.error(message) 
        elif level=="critical":
            Log._logger.critical("Internet is down") 
        else:
            raise ValueError("Invalid level: ", level)
