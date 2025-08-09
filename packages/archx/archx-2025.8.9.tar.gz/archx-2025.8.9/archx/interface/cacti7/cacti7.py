import subprocess, os, time, random, copy

from collections import OrderedDict

from loguru import logger


def cacti7_run(
    mem_type: str,
    tech_node_nm: str,
    cfg_dict: OrderedDict,
    origin_cfg_file=None,
    target_cfg_file=None,
    result_file=None
):
    """
    run the cacti with input configuration, work for SRAM, whose size is either calculated to match the bw or pre-specified
    """
    original = open(origin_cfg_file, 'r')
    target   = open(target_cfg_file, 'w')

    tech_node_um = float(int(tech_node_nm)/1000)

    if mem_type == 'sram':
        bank_count = int(cfg_dict['bank'])
        block_bits = int(cfg_dict['width'])
        block_bytes = int(cfg_dict['width'] / 8)
        total_bytes = int(bank_count * cfg_dict['depth'] * block_bytes)

        target.write('-size (bytes) ' + str(total_bytes) + '\n')
        target.write('-block size (bytes) ' + str(block_bytes) + '\n')
        target.write('-technology (u) ' + str(tech_node_um) + '\n')
        target.write('-UCA bank count '+ str(bank_count) + '\n')
        target.write('-output/input bus width ' + str(block_bits) + '\n')

    elif mem_type in ['dram', 'ddr4']:
        total_bytes = int(cfg_dict['size'] / 8)
        page_bits = 8192
        bank_count = 8
        prefetch = 8

        target.write('-size (bytes) ' + str(total_bytes) + '\n')
        target.write('-page size (bits) ' + str(page_bits) + '\n')
        target.write('-technology (u) ' + str(tech_node_um) + '\n')
        target.write('-UCA bank count '+ str(bank_count) + '\n')
        target.write('-internal prefetch width '+ str(prefetch) + '\n')
    
    for entry in original:
        target.write(entry)
    
    original.close()
    target.close()

    run_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'include/cacti7')
    if not os.path.exists(os.path.join(run_dir, 'cacti')):
        subprocess.call(['make', 'all'], shell=True, cwd=run_dir)
        time.sleep(10)
    
    tartget_cacti_name = result_file.replace('//', '/').replace('/', '_').split('.')[0] + '_'
    tartget_cacti_name += str(time.time())

    rep_cmd = 'cp ./cacti ./cacti_' + tartget_cacti_name
    subprocess.call([rep_cmd], shell=True, cwd=run_dir)
    final_cmd = './cacti_' + tartget_cacti_name + ' -infile ' + target_cfg_file + ' > ' + result_file
    subprocess.call([final_cmd], shell=True, cwd=run_dir)
    rm_cmd = 'rm -rf ./cacti_' + tartget_cacti_name
    subprocess.call([rm_cmd], shell=True, cwd=run_dir)


def parse_report_line_count(
    report=None,
    index=64
):
    # get the area and power numbers in the report for final memory power and energy estimation.
    cacti_out = open(report, 'r')
    line_idx = 0
    for entry in cacti_out:
        line_idx += 1
    broken_rpt = line_idx <= index
    return broken_rpt


def parse_report_sram(
    report=None
):
    # get the area and power numbers in the report for final memory power and energy estimation.
    cacti_out = open(report, 'r')

    line_idx = 0
    for entry in cacti_out:
        line_idx += 1
        if line_idx == 12:
            ram_type = entry.strip().split(':')[-1].strip()
            assert ram_type == 'Scratch RAM', 'Invalid SRAM type.'
        if line_idx == 50:
            # unit: ns
            bank = float(entry.strip().split(':')[-1].strip())
        if line_idx == 58:
            # unit: ns
            access_time = float(entry.strip().split(':')[-1].strip())
        if line_idx == 59:
            # unit: ns
            cycle_time = float(entry.strip().split(':')[-1].strip())
        if line_idx == 60:
            # unit: nJ
            dynamic_energy_rd = float(entry.strip().split(':')[-1].strip())
        if line_idx == 61:
            # unit: nJ
            dynamic_energy_wr = float(entry.strip().split(':')[-1].strip())
        if line_idx == 62:
            # unit: mW
            leakage_power_bank = float(entry.strip().split(':')[-1].strip())
        if line_idx == 63:
            # unit: mW
            gate_leakage_power_bank = float(entry.strip().split(':')[-1].strip())
        if line_idx == 64:
            # unit: mm^2
            height = float(entry.strip().split(':')[-1].split('x')[0].strip())
            width = float(entry.strip().split(':')[-1].split('x')[1].strip())
            area = height * width

        if line_idx == 2:
            # unit: byte
            block_sz_bytes = float(entry.strip().split(':')[-1].strip())
    
    broken_rpt = parse_report_line_count(report, 64)
    assert not broken_rpt, logger.error('Check ' + report + ' for sram cacti failure.')

    # MHz
    max_freq = 1 / cycle_time * 1000
    # nJ
    energy_per_rd_nJ = dynamic_energy_rd
    # nJ
    energy_per_wr_nJ = dynamic_energy_wr
    # mW
    leakage_power_mW = (leakage_power_bank + gate_leakage_power_bank) * bank
    # mm^2
    total_area_mm2 = area
    cacti_out.close()
    return energy_per_rd_nJ, energy_per_wr_nJ, leakage_power_mW, total_area_mm2, block_sz_bytes, max_freq


def parse_report_dram(
    report=None
):
    # get the area and power numbers in the report for final memory power and energy estimation.
    cacti_out = open(report, 'r')

    line_idx = 0
    for entry in cacti_out:
        line_idx += 1
        if line_idx == 12:
            ram_type = entry.strip().split(':')[-1].strip()
            assert ram_type == 'Scratch RAM', 'Invalid DRAM type.'
        if line_idx == 50:
            # unit: ns
            bank = float(entry.strip().split(':')[-1].strip())
        if line_idx == 58:
            # unit: ns
            access_time = float(entry.strip().split(':')[-1].strip())
        if line_idx == 59:
            # unit: ns
            cycle_time = float(entry.strip().split(':')[-1].strip())
        if line_idx == 61:
            # unit: nJ
            activate_energy = float(entry.strip().split(':')[-1].strip())
        if line_idx == 62:
            # unit: nJ
            energy_rd = float(entry.strip().split(':')[-1].strip())
        if line_idx == 63:
            # unit: nJ
            energy_wr = float(entry.strip().split(':')[-1].strip())
        if line_idx == 64:
            # unit: nJ
            precharge_energy = float(entry.strip().split(':')[-1].strip())
        if line_idx == 65:
            # unit: mW
            leakage_power_closed_page = float(entry.strip().split(':')[-1].strip())
        if line_idx == 66:
            # unit: mW
            leakage_power_open_page = float(entry.strip().split(':')[-1].strip())
        if line_idx == 67:
            # unit: mW
            leakage_power_IO = float(entry.strip().split(':')[-1].strip())
        if line_idx == 68:
            # unit: mW
            refresh_power = float(entry.strip().split(':')[-1].strip())
        if line_idx == 69:
            # unit: mm^2
            height = float(entry.strip().split(':')[-1].split('x')[0].strip())
            width = float(entry.strip().split(':')[-1].split('x')[1].strip())
            area = height * width

    broken_rpt = parse_report_line_count(report, 69)
    assert not broken_rpt, logger.error('Check ' + report + ' for dram cacti failure.')

    # MHz
    max_freq = 1 / cycle_time * 1000
    cacti_out.close()
    return activate_energy, energy_rd, energy_wr, precharge_energy, leakage_power_closed_page, leakage_power_open_page, leakage_power_IO, refresh_power, area, max_freq


def query(name: str, interface: str, query: OrderedDict, input_dir=None, output_dir=None):
    query = copy.deepcopy(query)
    query_class = query['class'].lower()
    query_technology = query['technology']
    query_frequency = query['frequency']
    del query['class']
    del query['technology']
    del query['frequency']

    assert os.path.isdir(output_dir), logger.error(f'Invalid output dir <{output_dir}>.')

    origin_cfg_file = os.path.dirname(os.path.abspath(__file__))
    assert query_class in ['sram', 'dram', 'ddr4'], logger.error(f'Invalid <{query_class}> in CACTI7; valid values: [sram, dram, ddr4]')
    if query_class == 'sram':
        origin_cfg_file = origin_cfg_file + '/sram.cfg'
    elif query_class in ['dram', 'ddr4']:
        origin_cfg_file = origin_cfg_file + '/ddr4.cfg'
    assert os.path.isfile(origin_cfg_file), logger.error(f'Invalid CACTI7 config file <{origin_cfg_file}>.')
    
    if query_class == 'sram':
        post_fix = '.sram' + '.width' + str(query['width']) + '.depth' + str(query['depth']) + '.bank' + str(query['bank'])
    elif query_class in ['dram', 'ddr4']:
        post_fix = '.ddr4' + '.size' + str(query['size'])

    target_cfg_file = os.path.join(output_dir, name + post_fix + '.cacti7.cfg')
    cacti_report = os.path.join(output_dir, name + post_fix + '.cacti7.rpt')

    target_cfg_file_flag = target_cfg_file + '.flag'
    if not os.path.exists(target_cfg_file_flag):
        cacti7_run(query_class, query_technology, query, origin_cfg_file, target_cfg_file, cacti_report)
        f = open(target_cfg_file_flag, 'a')
        f.write(target_cfg_file_flag)
        f.close()
    else:
        broken_rpt = parse_report_line_count(cacti_report, 64)
        if broken_rpt:
            os.remove(cacti_report)
            os.remove(target_cfg_file_flag)
            cacti7_run(query_class, query_technology, query, origin_cfg_file, target_cfg_file, cacti_report)

    if query_class == 'sram':
        energy_per_rd_nJ, energy_per_wr_nJ, leakage_power_mW, total_area_mm2, _, _ = parse_report_sram(cacti_report)
    elif query_class in ['dram', 'ddr4']:
        activate_energy, energy_rd, energy_wr, precharge_energy, leakage_power_closed_page, leakage_power_open_page, leakage_power_IO, refresh_power, area, max_freq = parse_report_dram(cacti_report)
        
        if 'embedded' not in query or query['embedded'] is False:
            IO_power_factor = 1.
        else:
            IO_power_factor = 0.

        bank_count = 8
        constant_power = (leakage_power_IO * IO_power_factor + refresh_power) * bank_count

        if 'open_page' not in query or query['open_page'] is False:
            constant_power = constant_power + leakage_power_closed_page * bank_count
        else:
            # default to open page
            constant_power = constant_power + leakage_power_open_page * bank_count
        
        energy_per_rd_nJ = energy_rd
        energy_per_wr_nJ = energy_wr
        leakage_power_mW = constant_power
        total_area_mm2 = area

    output_dict = OrderedDict()
    output_dict['technology'] = OrderedDict({'value': query_technology, 'unit': 'nm'})
    output_dict['frequency'] = OrderedDict({'value': query_frequency, 'unit': 'MHz'})
    output_dict['dynamic_energy'] = OrderedDict({'read': OrderedDict({'value': energy_per_rd_nJ, 'unit': 'nJ'}),
                                                 'write': OrderedDict({'value': energy_per_wr_nJ, 'unit': 'nJ'})})
    output_dict['leakage_power'] = OrderedDict({'value': leakage_power_mW, 'unit': 'mW'})
    output_dict['area'] = OrderedDict({'value': total_area_mm2, 'unit': 'mm^2'})

    return output_dict


if __name__ == '__main__':
    pass
