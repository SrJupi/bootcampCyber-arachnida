import time

def ft_progress(listy, bar_size=20, load_str="|\-/"):
    if not isinstance(bar_size, int):
        bar_size = 20
    load_str = str(load_str)
    str_size = len(load_str)
    start_time = time.time()
    size = len(listy)
    width = len(str(size))
    prog_str = '>'.ljust(bar_size)
    next_step = 1/bar_size
    other_step = 0.2/bar_size
    load_char = load_str[0]
    j = 1
    for i, item in enumerate(listy):
        progress = (i + 1)/size
        if progress > next_step:
            while next_step < progress:
                prog_str = '=' + prog_str[0:-1]
                next_step += 1/bar_size
        if progress > other_step:
            load_char = load_str[j % str_size]
            j += 1
            other_step += 0.2/bar_size
        diff_time = time.time() - start_time
        remain_time = (1 - progress) * (diff_time / progress)
        if remain_time > 60:
            remain_time /= 60
            remain_time = f"{remain_time:6.2f} min"
        else:
            remain_time = f"{remain_time:6.2f} s  "
        if diff_time > 60:
            diff_time /= 60
            diff_time = f"{diff_time:6.2f} min"
        else:
            diff_time = f"{diff_time:6.2f} s  "
        if i == size:
            load_char = 'OK!'
        print(f"\r-> ETA: {remain_time} [{prog_str[0:int(bar_size/2)]} {progress*100:6.2f}% {prog_str[int(bar_size/2):]}] {i+1:{width}d}/{size:{width}d} | elapsed time: {diff_time}  {load_char}", end = '')

        yield item

if __name__ == '__main__':
    
    listy = range(500)
    ret = 0
    for elem in ft_progress(listy):
        ret += elem
        time.sleep(0.005)
    print()
    print(ret)
