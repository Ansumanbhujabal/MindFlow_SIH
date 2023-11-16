from pymongo import MongoClient
from application_logging.logger import logger
import pandas as pd
import csv

logger = logger('log_Files/Database.log')

# 04U5TN3d9kI62EIJ


class dataBaseOperation:

    def __init__(self):

        logger.info('INFO', 'Trying To Connect With The Database')
        self.database_name = 'credit'
        self.collection_name = 'credit_data'

        # MongoDB connection string, replace it with your connection string
        self.mongo_uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/test?retryWrites=true&w=majority"

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]

        logger.info('INFO', 'The Connection Is Created')

    def use_database(self):
        try:
            logger.info('INFO', 'Using The Database')
            self.db = self.client[self.database_name]
            logger.info('INFO', 'The {database_name} Is Selected'.format(
                database_name=self.database_name))
        except Exception as e:
            raise Exception(
                f"(useDatabase) - There Is Something Wrong About useDatabase Method \n" + str(e))

    def create_collection(self):
        try:
            logger.info(
                'INFO', 'Collection Is Creating Inside The Selected Database')
            self.use_database()
            logger.info('INFO', 'The {collection_name} Is Created Inside The {database_name}'.format(
                collection_name=self.collection_name, database_name=self.database_name))
        except Exception as e:
            raise Exception(
                f"(createCollection) - There Is Something Wrong About Creating Collection Method \n" + str(e))

    def insert_into_collection(self):
        try:
            logger.info('INFO', 'Inserting The Data Into Database')
            file = "SouthGermanCredit\SouthGermanCredit.csv"
            with open(file, mode='r') as f:
                next(f)

                reader = csv.reader(f, delimiter='\n')
                for i in reader:
                    data = [int(value) for value in i[0].split(',')]
                    self.use_database()
                    self.collection.insert_one({
                        'ID': data[0],
                        'status': data[1],
                        'duration': data[2],
                        'credit_history': data[3],
                        'purpose': data[4],
                        'amount': data[5],
                        'savings': data[6],
                        'employment_duration': data[7],
                        'installment_rate': data[8],
                        'personal_status_sex': data[9],
                        'other_debtors': data[10],
                        'present_residence': data[11],
                        'property': data[12],
                        'age': data[13],
                        'other_installment_plans': data[14],
                        'housing': data[15],
                        'number_credits': data[16],
                        'job': data[17],
                        'people_liable': data[18],
                        'telephone': data[19],
                        'foreign_worker': data[20],
                        'credit_risk': data[21]
                    })

                logger.info('INFO', 'All The Data Entered Into The {database_name} Having Collection Name {collection_name}'.
                            format(database_name=self.database_name, collection_name=self.collection_name))
        except Exception as e:
            raise Exception(
                f"(insertIntoCollection) - There Is Something Wrong About Insert Into Data Method \n" + str(e))

    def get_data_from_database(self):
        try:
            logger.info('INFO', 'Trying To Get The Data From The Database')
            cursor = self.collection.find({})
            df = pd.DataFrame(list(cursor))
            logger.info(
                'INFO', 'We Gathered The Data From Database {}'.format(df))
        except Exception as e:
            raise Exception(
                f"(getData) - There Is Something Wrong About getData Method \n" + str(e))
