# -*- coding: utf-8 -*-
import logging
import time

# if you open the initializer feature, please implement the initializer function, as below:
# def initializer(context):
#   logger = logging.getLogger()
#   logger.info('initializing')

def handler(event, context):
  logger = logging.getLogger()
  logger.info('before sleep')
  time.sleep(2*50)
  logger.info('after sleep')
  return {'hello': 'world'}