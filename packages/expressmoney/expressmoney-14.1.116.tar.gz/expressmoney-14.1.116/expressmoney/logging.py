import logging

from pythonjsonlogger import jsonlogger


class YandexLoggingFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(YandexLoggingFormatter, self).add_fields(log_record, record, message_dict)
        log_record['logger'] = record.name
        log_record['level'] = str.replace(str.replace(record.levelname, "WARNING", "WARN"), "CRITICAL", "FATAL")


class YandexStreamHandler(logging.StreamHandler):
    def format(self, record):
        self.formatter = YandexLoggingFormatter('%(message)s %(level)s %(logger)s')
        return super().format(record)
