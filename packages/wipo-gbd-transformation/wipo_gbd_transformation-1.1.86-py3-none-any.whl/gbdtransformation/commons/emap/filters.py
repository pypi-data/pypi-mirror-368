ignore_namespace = ['http://www.euipo.europa.eu/EUTM/EUTM_Download']

def create_full_name(name): 
	result = ""
	
	if name.FirstName: 
		result += name.FirstName + " "
	if name.LastName:
		result += name.LastName
	if name.OrganizationName and name.OrganizationName != name.LastName and name.OrganizationName != result:
		if name.FirstName or name.LastName:
			result += ", "
		result += name.OrganizationName
	return result

	