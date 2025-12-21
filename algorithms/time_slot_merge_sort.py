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
        # Converts start times into minutes for comparison
        leftStartTime = toMinutes(sortedLeft[leftPointer].getStartTime())
        rightStartTime = toMinutes(sortedRight[rightPointer].getStartTime())

        if leftStartTime <= rightStartTime:
            mergedList.append(sortedLeft[leftPointer])
            leftPointer = leftPointer + 1
        else:
            mergedList.append(sortedRight[rightPointer])
            rightPointer = rightPointer + 1

    while leftPointer < len(sortedLeft):
        mergedList.append(sortedLeft[leftPointer])
        leftPointer = leftPointer + 1

    while rightPointer < len(sortedRight):
        mergedList.append(sortedRight[rightPointer])
        rightPointer = rightPointer + 1

    return mergedList

if __name__ == "__main__":
    class DummySlot:
        def __init__(self, startTime):
            self.startTime = startTime

        def getStartTime(self):
            return self.startTime

    inputList = []
    done = False
    while not done:
        addToList = input("Enter a time: ")
        if addToList == "done":
            done = True
        else:
            inputList.append(DummySlot(addToList))

    print([slot.getStartTime() for slot in inputList])
    sortedList = timeSlotMergeSort(inputList)
    print([slot.getStartTime() for slot in sortedList])
