from predict import predict
from services import datamanager, build_excel_sheet

# Run the test with optional CSV file argument

def sort_predictions(prediction, prediction_dic):
    return [key for key, value in prediction_dic.items() if prediction in value]

if __name__ == "__main__":
    #remove the old dq matrix if it exists
    datamanager.remove_old_dq_matrix()

    file_locations, file_names = datamanager.get_inbound_file_list()


    for i in range(0, len(file_locations)):
        prediction_dic = predict(file_locations[i])
        names = sort_predictions('Name', prediction_dic)
        numbers = sort_predictions('Number', prediction_dic)
        phones = sort_predictions('Phone', prediction_dic)
        addresses = sort_predictions('Address', prediction_dic)
        cities = sort_predictions('City', prediction_dic)
        states = sort_predictions('State', prediction_dic)
        countries = sort_predictions('Country', prediction_dic)
        postal_codes = sort_predictions('Zip', prediction_dic)
        emails = sort_predictions('Email', prediction_dic)
        unknown = sort_predictions('Unknown', prediction_dic)
        if i == 0: # build the definition sheet on first iteration
            build_excel_sheet.build_definition_sheet()

        build_excel_sheet.build_excel_sheet(file_names[i], names, numbers, phones, addresses, cities, states, countries, postal_codes, emails, unknown)

