Module Smoother
    '
    ' LOWESS - Locally Weighted Scatterplot Smoothing
    '
    ' X: upward sorted array of temporal values
    ' Y: values of IBI for each X
    '
    ' THIS INSTANCE smooths a sparse low-resolution scatter into a high-resolution curve
    '
    Public Function Lowess(ByVal X As Object, ByVal Y As Object, ByVal nPts As Long) As Double()

        Dim i, iMin, iMax, iPoint As Long
        Dim maxDist, SumWts, SumWtX, SumWtX2, SumWtY, SumWtXY, Denom, WLRSlope, WLRIntercept As Double

        Dim yLoess(LAST_SAMPLE) As Double

        Dim LastIndex = X.GetUpperBound(0)
        Dim distance(LastIndex) As Double
        Dim weight(LastIndex) As Double

        For iPoint = 0 To LAST_SAMPLE

            For i = 0 To LastIndex
                distance(i) = Math.Abs(X(i) - iPoint) ' populate x, y, distance
            Next

            iMin = 0
            iMax = LastIndex

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
                SumWtY = SumWtY + Y(i) * weight(i)
                SumWtXY = SumWtXY + X(i) * Y(i) * weight(i)
            Next
            Denom = SumWts * SumWtX2 - SumWtX ^ 2

            ' calculate the regression coefficients, and finally the loess value
            WLRSlope = (SumWts * SumWtXY - SumWtX * SumWtY) / Denom
            WLRIntercept = (SumWtX2 * SumWtY - SumWtX * SumWtXY) / Denom
            yLoess(iPoint) = WLRSlope * iPoint + WLRIntercept
		Next

        Return yLoess

    End Function

    '
    ' LOWESS2 - Locally Weighted Scatterplot Smoothing
    '
    ' X: upward sorted array of temporal values
    ' Y: values of IBI for each X
    '
    ' THIS INSTANCE smooths a sparse low-resolution scatter into another low-resolution scatter
    '
	Public Sub Lowess2(ByRef X As Object, ByRef Y As Object, ByRef Z As Object, ByVal nPts As Long)

		Dim i, iMin, iMax, iPoint As Long
		Dim xNow, maxDist, SumWts, SumWtX, SumWtX2, SumWtY, SumWtXY, Denom, WLRSlope, WLRIntercept As Double

		' set LastIndex to the lowest of the three input array's upper bound
		Dim LastIndex = X.GetUpperBound(0)
		If Y.GetUpperBound(0) < LastIndex Then LastIndex = Y.GetUpperBound(0)
		If Z.GetUpperBound(0) < LastIndex Then LastIndex = Z.GetUpperBound(0)

		Dim distance(LastIndex + 1) As Double
		Dim weight(LastIndex + 1) As Double

		For iPoint = 0 To LastIndex

			xNow = X(iPoint)

			For i = 0 To LastIndex
				distance(i) = Math.Abs(X(i) - xNow)	' populate x, y, distance
			Next

			iMin = 0
			iMax = LastIndex

			Dim loPts = iPoint * 2 + 1
			Dim hiPts = (LastIndex - iPoint) * 2 + 1
			Dim ourPts = nPts
			'If (loPts < ourPts) Then ourPts = loPts
			'If (hiPts < ourPts) Then ourPts = hiPts

			Do
				' find the nPts points closest to xNow
				If iMax + 1 - iMin <= ourPts Then Exit Do
				If distance(iMin) > distance(iMax) Then
					' remove first point
					iMin = iMin + 1
				ElseIf distance(iMin) < distance(iMax) Then
					' remove last point
					iMax = iMax - 1
				Else
					' remove both points
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
				SumWtY = SumWtY + Y(i) * weight(i)
				SumWtXY = SumWtXY + X(i) * Y(i) * weight(i)
			Next
			Denom = SumWts * SumWtX2 - SumWtX ^ 2

			' calculate the regression coefficients, and finally the loess value
			If Denom Then
				WLRSlope = (SumWts * SumWtXY - SumWtX * SumWtY) / Denom
				WLRIntercept = (SumWtX2 * SumWtY - SumWtX * SumWtXY) / Denom
				Z(iPoint) = WLRSlope * xNow + WLRIntercept
			Else
				Z(iPoint) = xNow
			End If

			ProgressBar = iPoint / LastIndex * 100
		Next

	End Sub

End Module
