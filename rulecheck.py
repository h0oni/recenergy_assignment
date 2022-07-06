import pip

try:
    import pandas as pd
except ModuleNotFoundError:
    pip._internal.main(['install', 'pandas'])
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    pip._internal.main(['install', 'tqdm'])

def redo_string(s):
  if s[0] in ('1', '0', 'Z'):
    return ((0,0), s)
  s = s[::-1]
  ch_tmp = s[0]
  flag = 0
  counter = {'LXH' : 0, 'HXL' : 0}
  for (idx,ch) in enumerate(s[1:]):
    if ch == ch_tmp and ch != 'X':
      flag = 1
    elif ch == 'X' : flag = 0
    else:
      if flag: 
        s[idx] = 'X'
        if ch == 'L' : counter['LXH'] += 1
        elif ch == 'H' : counter['HXL'] += 1
        flag = 0
    ch_tmp = ch
  return ((counter['HXL'], counter['LXH']), s[::-1])

def main():
    data = []
    column_flag = 1
    print('Reading data into a pandas dataframe')
    pbar = tqdm(total = 20001)
    with open('pat_s', 'r') as file:
        while(True):
            line = file.readline()
            if column_flag:
                columns = line[:-2].split()[1:]
                column_flag = 0
                continue
            pbar.update(1)
            if not line:
                break;
            line = line[9:].strip()
            data.append(list(line[:-1]))
    pbar.close()

    df = pd.DataFrame(data,columns = columns)
    del data, line, column_flag

    res_df = pd.DataFrame(columns = ['FORMAT'])
    counter = []
    print('Updating the patterns for each pin')
    for column in tqdm(columns):
        count, res_df[column] = redo_string(list(df[column]))
        counter.append(count)
    res_df['FORMAT'] = ['R1 dummy ']*len(df)

    with open('pat_s_rc','w') as file:
        file.write(' '.join(ch for ch in list(res_df))+';\n')
        print('Writing the new pattern file')
        for i in tqdm(range(len(df))):
            file.write(''.join(ch for ch in res_df.iloc[i].tolist())+';\n')
    file.close()

    with open('pat_s_logout', 'w') as file:
        print('Creating the logout file')
        for idx, column in enumerate(tqdm(columns)):
            file.write(f'{column} \t \'HLL\' to \'HXL\' : {counter[idx][0]} times. \t \'LHH\' to \'LXH\' : {counter[idx][1]} times\n')
    file.close

if __name__=="__main__":
    main()