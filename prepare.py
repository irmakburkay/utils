import os
import shutil
import argparse
from zipfile import ZipFile

try:
    import splitfolders
except ImportError:
    print("splitfolders not found, to install splitfolders => pip install split-folders")
    exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="directory with the input data. The directory needs to have the labels as sub-directories. In those sub-directories are then the actual files that gets split.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="output",
        help="name of output folders after splitting, defaults to `output`",
    )
    parser.add_argument(
        "--ratio",
        nargs="+",
        type=float,
        default=(0.8, 0, 0.2),
        help="the ratio of train val test, default is '0.8 0 0.2'",
    )

    args = parser.parse_args()

    if sum(args.ratio) != 1.0:
        print('Sum of ratios must equal to 1.0')
        exit()

    if args.ratio[0] == 0:
        print('Train ratio must be greater than 0')
        exit()

    path = os.path.abspath(args.input)
    folder = os.path.split(path)[0]
    output = os.path.join(folder, args.name)

    if os.path.exists(output):
        i = 1
        while os.path.exists(output + '_' + str(i)):
            i += 1
        output += '_' + str(i)


    temp = os.path.join(folder, 'temp')

    if os.path.exists(temp):
        i = 1
        while os.path.exists(temp + '_' + str(i)):
            i += 1
        temp += '_' + str(i)


    with ZipFile(args.input, 'r') as obj:
        obj.extractall(path=temp)

    obj_path = os.path.join(temp, 'obj_train_data')

    listdir = os.listdir(os.path.join(obj_path))

    if not os.path.exists(os.path.join(obj_path, 'labels')):
        os.makedirs(os.path.join(obj_path, 'labels'))
    if not os.path.exists(os.path.join(obj_path, 'images')):
        os.makedirs(os.path.join(obj_path, 'images'))


    for dir in listdir:
        if dir.endswith('.txt'):
            shutil.move(os.path.join(obj_path, dir), os.path.join(obj_path, 'labels', dir))
        else:
            shutil.move(os.path.join(obj_path, dir), os.path.join(obj_path, 'images', dir))


    splitfolders.ratio(obj_path, output=output, ratio=args.ratio)

    yaml = f"train: {os.path.join(output, 'train', 'images')}\n"
    
    if args.ratio[1] != 0:
        yaml += f"val: {os.path.join(output, 'val', 'images')}\n"
    else:
        shutil.rmtree(os.path.join(output, 'val'))

    if args.ratio[2] != 0:
        yaml += 'val: ' if args.ratio[1] == 0 else 'test: '
        yaml += f"{os.path.join(output, 'test', 'images')}\n"
    else:
        shutil.rmtree(os.path.join(output, 'test'))

    with open(os.path.join(temp, 'obj.data'), 'r') as f:
        line = f.readline()
        line = line.split('=')
        num_classes = (int(line[1]))
        yaml += f'\n# number of classes \nnc: {num_classes} \n'

    with open(os.path.join(temp, 'obj.names'), 'r') as f:
        lines = [line.rstrip() for line in f]
        yaml += f'\n# class names \nnames: {lines}'

    with open(os.path.join(output, 'data.yaml'), 'w') as f:
        f.write(yaml)   

    shutil.rmtree(temp)

    print(f'Output saved to: {output}')