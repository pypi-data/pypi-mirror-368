# Introduction to SDT files

SDT file is a **binary** file to store a 2D array with column names. It can be splited into 2 parts, the **header** and the **body**.

The header part starts with a little-endian 32-bit integer $H$ (occupying 4 bytes), indicating the length of the header part (this number is excluded). 

The following $H$ bytes are the real header, which can be decoded as a UTF-8 string. The first character of the string indicates the data type. Details are shown in the following table:

|Character|Type|CType|
|---|---|---|
|b|int8|unsigned char|
|s|int16|short|
|i|int32|int|
|l|int64|long long|
|f|float32|float|
|d|float64|double|
|q|float128|long double|

From the second character on, this string stores the column names splited by `|`. Note that there may be space at the end of this string, which should be stripped. The space are used for padding to make the length of the header string a multiple of 4.

The rest of the file is the body part, whose length should be a multiple of `sizeof(data_type) * len(columns)`, storing the actual data of the table. The data follows **row-major** storage. Note the data is machine-specfic, which means **error occurs if data saved on a little-endian architecture is read on a big-endian architecture!**