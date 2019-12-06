import random

# a = [i for i in range(32)]
#
# origin = 31
# segment = 3
# end = origin + segment
# idxs = [i for i in range(origin, end)]
# for i in range(len(idxs)):
#     idxs[i] = idxs[i]%32
# print(idxs)

arr = [10 for i in range(10)]

print(arr)

if all([ar == arr[0] for ar in arr[1:]]):
    print('kitataaata')
else:
    print('=======')
