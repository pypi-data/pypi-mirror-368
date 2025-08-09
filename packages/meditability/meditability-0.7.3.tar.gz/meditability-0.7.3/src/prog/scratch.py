# == Native Modules

# == Installed Modules

# == Project Modules


def check_format(variable, data_type, paramater_name, default_value):
	dummy = True
	if isinstance(variable, data_type):
		if variable == default_value:
			print(f"Please specify a value for the option --{paramater_name}.")
			exit(0)
		if data_type == str:
			if not dummy:
				print(f"The string provided in --{paramater_name} is not a valid IUPAC representation: {variable}")
				exit(0)
		return data_type(variable)
	else:
		if data_type != str:
			try:
				data_type(variable)
				return data_type(variable)

			except ValueError:
				try:
					variable_list = variable.split(',')
					if len(variable_list) == 2:
						variable_list = [int(x) for x in variable_list]
						return list(variable_list)
					else:
						print(
							f"Invalid data type for {paramater_name}: '{variable}'. Please double-check the documentation.")
						exit(0)

				except ValueError:
					print(
						f"Invalid data type for {paramater_name}: '{variable}'. Please double-check the documentation.")
					exit(0)


def main():
	dsb_position = '6'
	a = check_format(dsb_position, int, 'dsb_pos', -10000)



if __name__ == "__main__":
	main()
