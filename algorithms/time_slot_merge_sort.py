def toMinutes(timeString: str):
    hoursString, minutesString = timeString.split(":")

    hours = int(hoursString)
    minutes = int(minutesString)

    totalMinutes = (hours * 60) + minutes
    return totalMinutes

def timeSlotMergeSort(slotList):
    # If the list has one or zero slots, it doesn't need sorting
    if len(slotList) <= 1:
        return slotList

    middleIndex = len(slotList) // 2
    leftHalf = slotList[:middleIndex]
    rightHalf = slotList[middleIndex:]

    # Uses recursion to sort both halves
    sortedLeft = timeSlotMergeSort(leftHalf)
    sortedRight = timeSlotMergeSort(rightHalf)

    mergedList = []
    leftPointer = 0
    rightPointer = 0

    while leftPointer < len(sortedLeft) and rightPointer < len(sortedRight):
        # Convert start times into minutes for comparison
        leftStartTime = toMinutes(sortedLeft[leftPointer].getStartTime())
        rightStartTime = toMinutes(sortedRight[rightPointer].getStartTime())

        if leftStartTime <= rightStartTime:
            mergedList.append(sortedLeft[leftPointer])
            leftPointer = leftPointer + 1
        else:
            mergedList.append(sortedRight[rightPointer])
            rightPointer = rightPointer + 1

    # Add any remaining slots from the left half
    while leftPointer < len(sortedLeft):
        mergedList.append(sortedLeft[leftPointer])
        leftPointer = leftPointer + 1

    # Add any remaining slots from the right half
    while rightPointer < len(sortedRight):
        mergedList.append(sortedRight[rightPointer])
        rightPointer = rightPointer + 1

    return mergedList