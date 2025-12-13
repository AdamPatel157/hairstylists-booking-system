def rotateRight(originalValue, numberOfBits):
    # Bitwise right shift
    shiftedRight = originalValue >> numberOfBits

    # Bitwise left shift
    shiftedLeft = originalValue << (32 - numberOfBits)

    # Bitwise OR
    combinedValue = shiftedRight | shiftedLeft

    limitedValue = combinedValue % (2 ** 32)

    return limitedValue

def hashPassword(getPassword):
    # Pre-processing Starts Here:
    # Takes each character from the user's password and converts to binary then joins them together
    binaryPassword = ""
    for character in getPassword:
        binaryPassword = binaryPassword + format(ord(character), '08b')

    binaryPassword = binaryPassword + '1'

    while len(binaryPassword) % 512 != 448:
        binaryPassword = binaryPassword + '0'
    binaryLength = format(len(getPassword) * 8, '064b')
    binaryPassword = binaryPassword + binaryLength

    # Initialises hash values with the square roots of the first 8 prime numbers in Hexadecimal
    h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
         0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

    # Initialises round constants
    # Creates a list of the cube roots of the first 64 prime numbers in Hexadecimal
    k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
         0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
         0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
         0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
         0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
         0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
         0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
         0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
         0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
         0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
         0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    messageSchedule = []

    # Breaks the binary password into 32‑bit chunks
    for chunkIndex in range(0, len(binaryPassword), 32):
        chunkBits = binaryPassword[chunkIndex:chunkIndex + 32]
        chunkValue = int(chunkBits, 2)
        messageSchedule.append(chunkValue)

    while len(messageSchedule) < 64:
        messageSchedule.append(0)

    for wordIndex in range(16, 64):
        rotate7 = rotateRight(messageSchedule[wordIndex - 15], 7)
        rotate18 = rotateRight(messageSchedule[wordIndex - 15], 18)
        shift3 = messageSchedule[wordIndex - 15] >> 3
        s0 = rotate7 ^ rotate18 ^ shift3

        rotate17 = rotateRight(messageSchedule[wordIndex - 2], 17)
        rotate19 = rotateRight(messageSchedule[wordIndex - 2], 19)
        shift10 = messageSchedule[wordIndex - 2] >> 10
        s1 = rotate17 ^ rotate19 ^ shift10

        newWord = messageSchedule[wordIndex - 16] + s0 + messageSchedule[wordIndex - 7] + s1

        newWord = newWord % (2 ** 32)

        messageSchedule[wordIndex] = newWord

    # Compression loop
    a, b, c, d, e, f, g, hTemp = h

    for roundIndex in range(0, 64):
        rotate6 = rotateRight(e, 6)
        rotate11 = rotateRight(e, 11)
        rotate25 = rotateRight(e, 25)
        S1 = rotate6 ^ rotate11 ^ rotate25

        eAndF = e & f
        notE = (2 ** 32 - 1) - e
        notEAndG = notE & g
        choice = eAndF ^ notEAndG

        temp1 = hTemp + S1 + choice + k[roundIndex] + messageSchedule[roundIndex]
        temp1 = temp1 % (2 ** 32)

        rotate2 = rotateRight(a, 2)
        rotate13 = rotateRight(a, 13)
        rotate22 = rotateRight(a, 22)
        S0 = rotate2 ^ rotate13 ^ rotate22

        aAndB = a & b
        aAndC = a & c
        bAndC = b & c
        majority = aAndB ^ aAndC ^ bAndC

        temp2 = S0 + majority
        temp2 = temp2 % (2 ** 32)

        # Calculates new values for each working variable
        newA = (temp1 + temp2) % (2 ** 32)
        newB = a
        newC = b
        newD = c
        newE = (d + temp1) % (2 ** 32)
        newF = e
        newG = f
        newH = g

        a = newA
        b = newB
        c = newC
        d = newD
        e = newE
        f = newF
        g = newG
        hTemp = newH

    # Updates the final hash values with the results
    h[0] = (h[0] + a) % (2 ** 32)
    h[1] = (h[1] + b) % (2 ** 32)
    h[2] = (h[2] + c) % (2 ** 32)
    h[3] = (h[3] + d) % (2 ** 32)
    h[4] = (h[4] + e) % (2 ** 32)
    h[5] = (h[5] + f) % (2 ** 32)
    h[6] = (h[6] + g) % (2 ** 32)
    h[7] = (h[7] + hTemp) % (2 ** 32)

    hexParts = []

    for value in h:
        hexString = format(value, '08x')
        hexParts.append(hexString)

    finalHash = ""
    for part in hexParts:
        finalHash = finalHash + part

    return finalHash


# For individual module testing purposes:

if __name__ == "__main__":
    getString = input("Enter your password: ")
    result = hashPassword(getString)
    print(result)