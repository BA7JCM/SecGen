#!/opt/labtainer/venv/bin/python3
import hashlib
import argparse
import os

global seed
def getMasterSeed(logger):
    global seed
    ''' hack until start.config really parsed '''
    if seed is None:
        start_config_file = '.local/config/start.config'
        if not os.path.isfile(start_config_file):
            logger.error('Could not find %s' % start_config_file)
            exit(1)
        with open(start_config_file) as fh:
            for line in fh:
                if line.strip().startswith('#'):
                    continue
                if 'LAB_MASTER_SEED' in line:
                    parts = line.strip.split()
                    seed = parts[1]
                    break
    return seed




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert hash_equal value to hashes and store in new goals.config file.  Reads from a goals.answers file that by default is in the simlab directory for source control purposes.')
    parser.add_argument('-i', '--input_file', action='store', help='Name of input goals file.  Defaults to $LABTAINER_DIR/../simlab/<lab>/goals.answers', metavar='')
    args = parser.parse_args()
    cur_dir = os.path.abspath(os.getcwd())
    if args.input_file is None:
        labname = os.path.basename(os.path.dirname(cur_dir))
        labtainer_dir = os.path.abspath(os.getenv('LABTAINER_DIR'))
        parent = os.path.dirname(labtainer_dir)
        answer_file = os.path.join(parent, 'simlab', labname, 'goals.answers')
        if not os.path.isfile(answer_file):
            print('No file found at %s.  Either use the -i option, or, preferably, put the goals.answers in simlab')
            exit(1)
    else:        
        answer_file = args.input_file
        print('Please consider moving your goals.answers to the simlab repo for source control.  Do not put it on GitHub!')
    config_file = 'goals.config'
    if not os.path.isfile(answer_file):
        print('No file named %s found.')
        exit(1)
    goals = open(config_file, 'w')
    goals.write('# DO NOT edit this file, it is generated by hash-goals.py.  Edit the goals.answers files instead.\n')
    with open(answer_file) as fh:
        for line in fh:
            if line.strip().startswith('#'):
                goals.write(line)
                continue
            parts = line.strip().split(':')
            if len(parts) >= 4:
                if parts[1].strip() == 'hash_equal':
                    if not parts[3].strip().startswith('answer='):
                        print('This type of comparison not yet supported, requires "answer="')
                        exit(1)
                    value = parts[3].strip().split('=')[1]
                    mymd5 = hashlib.new('md5')
                    mymd5.update(value.encode('utf-8'))
                    mymd5_hex_string = mymd5.hexdigest()
                    line = '%s : %s : %s : answer=%s\n' % (parts[0].strip(), parts[1].strip(), parts[2].strip(), mymd5_hex_string)
            goals.write(line)
    goals.close()
