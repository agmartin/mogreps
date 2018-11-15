import utils
from dimension_manager import DimensionManager
from fact_manager import FactManager

def main(event, context):
    print('event: ',event)

    # file_path = utils.get_file_from_event(event)

    file_path = '/tmp/prods_op_mogreps-g_20161231_18_22_003.nc'

    dm = DimensionManager(file_path)
    dm.check_dimension_info()
    ids = dm.get_dim_ids()

    fm = FactManager(file_path)
    fm.manage_fact_wbulb_freez_alt(ids)
    print('complete')

if __name__ == "__main__":
    import event
    main(event.test,'')
