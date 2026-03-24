Module RetiredCode

    Sub GetRmsCount(ByRef SampleSet As Array)

        Dim polarity As Boolean = (SampleSet(0, 2) > 0)

        RmsCount = 1    ' count the final run that ends the scan

        For n = 0 To LAST_SAMPLE
            If (polarity Xor (SampleSet(n, 2) > 0)) Then
                RmsCount = RmsCount + 1
                polarity = (SampleSet(n, 2) > 0)
            End If
        Next

        Console.WriteLine("RMS Count = " & RmsCount)

    End Sub

    Sub BuildRmsArrays(ByRef SampleSet As Array)

        Dim Polarity As Boolean = (SampleSet(0, 2) > 0), Sum As Double = 0, RmsMax = Double.MinValue, SampleCount As Integer

        SampleCount = 0
        Polarity = (SampleSet(0, 2) > 0)

        For n = 0 To LAST_SAMPLE
            If (Polarity Xor (SampleSet(n, 2) > 0)) Then
                RmsTime(RmsIndex) = n
                'Sum = Math.Sqrt(Sum / SampleCount)
                RmsVal(RmsIndex) = Sum
                If Sum > RmsMax And n > 100 And n < (LAST_SAMPLE - 100) Then
                    RmsMax = Sum
                End If
                RmsIndex = RmsIndex + 1
                Polarity = (SampleSet(n, 2) > 0)
                Sum = 0
                'SampleCount = 0
            End If
            Sum = Sum + Math.Abs(SampleSet(n, 2))
            'Sum = Sum + (SampleSet(n, 2) ^ 2)
            'SampleCount = SampleCount + 1
        Next

        RmsTime(RmsIndex) = LAST_SAMPLE
        RmsVal(RmsIndex) = Math.Abs(Sum)
        'RmsVal(RmsIndex) = Math.Sqrt(Sum / SampleCount)

        'incorporate half of each neighbor
        'For n = 1 To RmsIndex - 1
        'RmsVals(n) = (RmsVal(n - 1) * 0.5 + RmsVal(n) + RmsVal(n + 1) * 0.5) / 2
        'Next

        ' now we rescale the RmsVals array to 2*YSCALE
        Dim RmsScale = 2 * YSCALE / RmsMax
        For n = 1 To RmsIndex - 1
            RmsVal(n) = RmsVal(n) * RmsScale - YSCALE
        Next

        'Lowess2(RmsTime, RmsVals, RmsVal, 5)


        'RmsPower = Lowess(RmsTime, RmsVals, 7)

    End Sub

End Module
