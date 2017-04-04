from json import dump
from bson import ObjectId
import os
import paths

#Function to validate metadata fields
def validate_metadata(metadata):
	if metadata.get("mdf_source_name", None): #placeholder for valid metadata check
		return True
	else:
		return False

#Function to validate record fields
def validate_record(record):
	if record.get("mdf_source_name", None): #placeholder
		return True
	else:
		return False

#Validator class holds data about a dataset while writing to feedstock
class Validator:
	#init optionally takes dataset metadata to start processing and save another function call
	def __init__(self, metadata=None):
		self.__feedstock = None
		self.dataset_id = None

		if metadata:
			res = self.write_metadata(metadata)
			if not res["success"]:
				raise ValueError("Invalid metadata: '" + res["message"])

	#del attempts cleanup
	def __del__(self):
		try:
			self.__feedstock.close()
		except AttributeError: #Feedstock wasn't opened
			pass

	#Sets metadata for dataset if not already set
	def write_metadata(self, metadata):
		if self.__feedstock or self.dataset_id: #Metadata already set; cannot change
			return {"success" : False, "message" : "Metadata already written for this dataset"}

		md_val = validate_metadata(metadata)
		if md_val == False:
			return {"success" : False, "message" : "Invalid metadata"}

		#Open feedstock file for the first time and write metadata entry
		feedstock_path = paths.feedstock + metadata["mdf_source_name"] + "_all.json"
		metadata["mdf_id"] = str(ObjectId())
		try:
			self.__feedstock = open(feedstock_path, 'w')
			dump(metadata, self.__feedstock)
			self.__feedstock.write("\n")
			
			self.dataset_id = metadata["mdf_id"]

			return {"success" : True}

		except:
			return {"success" : False, "message" : "Error: Bad metadata"}

	#Output single record to feedstock
	def write_record(self, record):
		if validate_record(record) == False:
			return {"success" : False, "message" : "Error: Bad record"}

		record["mdf_id"] = str(ObjectId())
		record["parent_id"] = self.dataset_id

		#Write new record to feedstock
		try:
			dump(record, self.__feedstock)
			self.__feedstock.write("\n")
			return {"success" : True}
		except:
			return {"success" : False, "message" : "Error: Bad record"}

	#Output whole dataset to feedstock
	#all_records must be a list of all the dataset records
	def write_dataset(self, all_records):
		#Write all records to feedstock
		for record in all_records:
			result = self.write_record(record)
			if not result["success"]:
				print("Error on record: ", record)
		return {"success" : True}


