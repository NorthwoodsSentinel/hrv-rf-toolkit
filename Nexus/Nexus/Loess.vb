Module LOWESS
    '
    ' LOWESS - Locally Weighted Scatterplot Smoothing
    '
    ' X: upward sorted array of temporal values
    ' Y: values of IBI for each X
    '
    '
    '
    Public Function Lowess(ByVal X As Object, ByVal Y As Object, ByVal nPts As Long) As Double()

        Dim i, iMin, iMax, iPoint As Long
        Dim maxDist, SumWts, SumWtX, SumWtX2, SumWtY, SumWtXY, Denom, WLRSlope, WLRIntercept As Double

        Dim lastX As Long = X(X.GetUpperBound) ' get the last X value in the X values array

        Dim distance(lastX) As Double
        Dim weight(lastX) As Double
        Dim yLoess(lastX) As Double

        For iPoint = 0 To lastX

            For i = 0 To lastX
                distance(i) = Math.Abs(X(i) - iPoint) ' populate x, y, distance
            Next

            iMin = 0
            iMax = lastX

            Do
                ' find the nPts points closest to xNow
                If iMax + 1 - iMin <= nPts Then Exit Do
                If distance(iMin) > distance(iMax) Then
                    ' remove first point
                    iMin = iMin + 1
                ElseIf distance(iMin) < distance(iMax) Then
                    ' remove last point
                    iMax = iMax - 1
                Else
                    ' remove both points?
                    iMin = iMin + 1
                    iMax = iMax - 1
                End If
            Loop

            ' Find max distance
            maxDist = -1
            For i = iMin To iMax
                If distance(i) > maxDist Then maxDist = distance(i)
            Next

            ' calculate weights using scaled distances
            For i = iMin To iMax
                weight(i) = (1 - (distance(i) / maxDist) ^ 3) ^ 3
            Next

            ' do the sums of squares
            SumWts = 0
            SumWtX = 0
            SumWtX2 = 0
            SumWtY = 0
            SumWtXY = 0
            For i = iMin To iMax
                SumWts = SumWts + weight(i)
                SumWtX = SumWtX + X(i) * weight(i)
                SumWtX2 = SumWtX2 + (X(i) ^ 2) * weight(i)
                SumWtY = SumWtY + Y(i, 1) * weight(i)
                SumWtXY = SumWtXY + X(i) * Y(i) * weight(i)
            Next
            Denom = SumWts * SumWtX2 - SumWtX ^ 2

            ' calculate the regression coefficients, and finally the loess value
            WLRSlope = (SumWts * SumWtXY - SumWtX * SumWtY) / Denom
            WLRIntercept = (SumWtX2 * SumWtY - SumWtX * SumWtXY) / Denom
            yLoess(iPoint) = WLRSlope * iPoint + WLRIntercept

        Next

        LOWESS = yLoess

    End Function

End Module