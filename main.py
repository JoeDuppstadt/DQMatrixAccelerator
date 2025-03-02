from predict import predict
from services import datamanager, build_excel_sheet

# Run the test with optional CSV file argument

def sort_predictions(prediction, prediction_dic):
    return [key for key, value in prediction_dic.items() if prediction in value]

if __name__ == "__main__":
    #remove the old dq matrix if it exists
    datamanager.remove_old_dq_matrix()

    file_locations, file_names = datamanager.get_inbound_file_list()


    for i in range(0, len(file_locations)-1):
        prediction_dic = predict(file_locations[i])
        names = sort_predictions('Name', prediction_dic)
        numbers = sort_predictions('Number', prediction_dic)
        phones = sort_predictions('Phone', prediction_dic)
        #if i == 0: # build the definition sheet on first iteration
        #    build_excel_sheet.build_definition_sheet()

        build_excel_sheet.build_excel_sheet(file_names[i], names, numbers, phones)

