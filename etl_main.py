import os
import time
import utils
from dimension_manager import DimensionManager
from fact_manager import FactManager







if __name__ == '__main__':
    print('starting up')
    while True:
        print('entering main loop')
        file_key = utils.check_for_message()
        if file_key:
            print('found key')
            file_name = utils.get_file(file_key)
            print(file_name)

            # dm = DimensionManager(file_path)
            # dm.check_dimension_info()
            # ids = dm.get_dim_ids()

            # fm = FactManager(file_path)
            # fm.manage_fact_wbulb_freez_alt(ids)

            # test_data = fm.manage_fact_wbulb_freez_alt(ids)

        else:
            print('going to sleep')
            time.sleep(60)





