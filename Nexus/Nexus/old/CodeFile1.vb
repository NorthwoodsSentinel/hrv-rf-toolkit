Public Module ProcessingCode

    Public Sub ProcessData(ByRef SourceFile As String)

        SampleCount = GetSampleCount(SourceFile)

        If LAST_SAMPLE <> 0 Then SampleCount = LAST_SAMPLE + 1

        Console.WriteLine()
        Console.WriteLine("   File Sample Count: {0:D}", SampleCount)
        Console.WriteLine("Total Recording Secs: {0:F2}", SampleCount / 256)
        Console.WriteLine("                Mins: {0:F2}", SampleCount / 256 / 60)
        Console.WriteLine()

        Dim SampleSet(SampleCount, TRACE_COUNT)

        GetSampleSet(SourceFile, SampleSet)

        SanityCheckAndTrimSampleSet(SampleSet)

        LAST_SAMPLE = SampleCount - 1

        FilterBreathData(SampleSet) ' A 20Hz high-pass filter to remove DC bias from the breathing data

        Process_Raw_EKG(SampleSet)
        RemoveEctopicBeats(SampleSet)

        'RwaveCount = AddBeatInterlinkLines(SampleSet)
        RwaveCount = GetRwaveCount(SampleSet)
        'Console.WriteLine("R Wave Count = " & RwaveCount)

        Array.Resize(RwaveTime, RwaveCount)
        Array.Resize(RwaveVal, RwaveCount)
        Array.Resize(RwaveVals, RwaveCount)
        Array.Resize(RmsVal, RwaveCount)

        BuildRwaveArrays(SampleSet)
        WriteRtoRintervalFile(SourceFile, RwaveCount)
        'WriteHeartWaveFile(SourceFile, RwaveCount)

        'BuildRmsTimeline()

        'AverageAndInvertRwave()
        RebaseAndInvertRwaves()
        FindHrvPeaks()

        'WriteSmoothHeartFile(SourceFile, SampleSet)

        MeasurePeakToPeak()
        RescaleBR(SampleSet)
        RescaleHR()
        'SineWaveFit(SampleSet)

        FileProcessed = True

        PublicSampleSet = SampleSet

        'HrvDisplay.Display(SampleSet)

    End Sub
    'Sub WriteSmoothHeartFile(ByVal SourceFile As String, ByRef SampleSet As Array)

    'AveragingWindowSmoother(SampleSet, 4, 2, 11)

    'Dim RRintervalFile = Replace(SourceFile, ".txt", "-wave.dat")
    'Dim file = My.Computer.FileSystem.OpenTextFileWriter(RRintervalFile, False, System.Text.Encoding.ASCII)
    'For n = 0 To LAST_SAMPLE
    'file.WriteLine(SampleSet(n, 4))
    'Next
    'file.Close()

    'End Sub
    Function GetSampleCount(ByRef SourceFile As String) As Integer

        Dim InData = False, SampleCount = 0

        If InStr(SourceFile, ".dat") Then
            InData = True
        End If

        Using LineIn As New FileIO.TextFieldParser(SourceFile)
            LineIn.TextFieldType = FileIO.FieldType.Delimited
            LineIn.SetDelimiters(",", vbTab)
            While Not LineIn.EndOfData
                If InData Then
                    Try
                        Dim DatumCount = LineIn.ReadFields().Length
                        If DatumCount >= 2 And DatumCount <= 4 Then SampleCount = SampleCount + 1
                    Catch
                    End Try
                Else
                    If String.Compare(Left(LineIn.ReadLine, 6), "Sensor") = 0 Then InData = True
                End If
            End While
        End Using

        Return SampleCount

    End Function
    Sub GetSampleSet(ByRef SourceFile As String, ByRef TheSampleSet As Array)

        Dim InData = False, SampleNumber = 0

        If InStr(SourceFile, ".dat") Then
            InData = True
        End If

        Using LineIn As New FileIO.TextFieldParser(SourceFile)
            LineIn.TextFieldType = FileIO.FieldType.Delimited
            LineIn.SetDelimiters(",", vbTab)
            While Not LineIn.EndOfData
                If InData Then
                    Try
                        Dim Datums = LineIn.ReadFields()
                        If Datums.Length >= 2 And Datums.Length <= 4 Then
                            TheSampleSet(SampleNumber, 0) = Datums(0)
                            TheSampleSet(SampleNumber, 1) = Datums(1)
                            SampleNumber = SampleNumber + 1
                            If SampleNumber >= SampleCount Then Exit Sub
                        End If
                    Catch
                    End Try
                Else
                    If String.Compare(Left(LineIn.ReadLine, 6), "Sensor") = 0 Then InData = True
                End If
            End While
        End Using

    End Sub
    Sub SanityCheckAndTrimSampleSet(ByRef SampleSet As Array)
        ' this looks at the middle 90% of the session data to obtain the range
        ' of valid data for both channels. It then hunts outward from either
        ' end to the first sample which falls outsidee of the range found.

        Dim HR_Max = Double.MinValue, HR_Min = Double.MaxValue
        Dim BR_Max = Double.MinValue, BR_Min = Double.MaxValue

        Dim FirstSample = SampleCount * 0.2         ' we don't initially scan the first 5%
        Dim LastSample = SampleCount - FirstSample  ' we don't initially scan the final 5%
        For n = FirstSample To LastSample
            If SampleSet(n, 0) > HR_Max Then HR_Max = SampleSet(n, 0)
            If SampleSet(n, 0) < HR_Min Then HR_Min = SampleSet(n, 0)
            If SampleSet(n, 1) > BR_Max Then BR_Max = SampleSet(n, 1)
            If SampleSet(n, 1) < BR_Min Then BR_Min = SampleSet(n, 1)
        Next

        ' now we scan left from the left edge to find the first out-of-range sample sets
        Do
            If SampleSet(FirstSample, 0) > HR_Max Then Exit Do
            If SampleSet(FirstSample, 0) < HR_Min Then Exit Do
            If SampleSet(FirstSample, 1) > BR_Max Then Exit Do
            If SampleSet(FirstSample, 1) < BR_Min Then Exit Do
            FirstSample = FirstSample - 1
        Loop While FirstSample > 0

        ' now we scan right from the right edge to find the first out-of-range sample sets
        Do
            If SampleSet(LastSample, 0) > HR_Max Then Exit Do
            If SampleSet(LastSample, 0) < HR_Min Then Exit Do
            If SampleSet(LastSample, 1) > BR_Max Then Exit Do
            If SampleSet(LastSample, 1) < BR_Min Then Exit Do
            LastSample = LastSample + 1
        Loop While LastSample < SampleCount

        Console.WriteLine("Original Sample Count: {0:D}", SampleCount)
        SampleCount = LastSample - FirstSample + 1  ' update our sample count
        Console.WriteLine(" Trimmed Sample Count: {0:D}", SampleCount)

        'Console.WriteLine("HR Min: {0:F2}", HR_Min)
        'Console.WriteLine("HR Max: {0:F2}", HR_Max)
        'Console.WriteLine("BR Min: {0:F2}", BR_Min)
        'Console.WriteLine("BR Max: {0:F2}", BR_Max)

        ' check to see whether we have anything to trim from the front of the array?
        If FirstSample Then
            ' we =do= have something to trim from the front of the array,
            ' so let's copy the first valid sample down to the front of the array...
            For n = 0 To SampleCount - 1
                SampleSet(n, 0) = SampleSet(n + FirstSample, 0)
                SampleSet(n, 1) = SampleSet(n + FirstSample, 1)
            Next
        End If
    End Sub
    Sub FilterBreathData(ByRef SampleSet As Array)
        ' This is a high-pass filter with a very low corner frequency of 0.05Hz
        ' (20 second response time). It is used to AC-couple the breathing to
        ' normalize and bring it down to a zero centerline. It is designed to
        ' introduce negligible phase shift into the breath data.
        '
        ' https://www-users.cs.york.ac.uk/~fisher/mkfilter/trad.html
        ' 
        ' Chebyshev - Highpass - 256 samples/sec - (-1 dB ripple) Corner Freq 0.05Hz

        Dim xv0, xv1, yv0, yv1 As Double

        xv1 = SampleSet(0, 1)

        For n = 0 To LAST_SAMPLE
            xv0 = xv1
            xv1 = SampleSet(n, 1) / 1.000312225
            yv0 = yv1
            yv1 = xv1 - xv0 + 0.9993757454 * yv0
            SampleSet(n, 1) = yv1
        Next
    End Sub
    Sub Process_Raw_EKG(ByRef SampleSet As Array)
        ' This takes in the raw EKG and returns an Array of inter-beat intervals

        ' 0: Raw HR Source Data
        ' 2: dv/dt encoded HR
        ' 3: ROI (region of interest) data
        ' 4: R-Wave Point

        ' INPUT: 0 / OUTPUT: 1

        'LogSamples(SampleSet, 0)

        Dim t0, t1, t2 As Double
        '
        ' This is a weighted dv/dt differentiator functioning as a history-weighted high-pass
        ' filter to move the EKG's DC component and preferentially feature-extract the R-Wave 
        ' 
        t0 = t1 = t2 = SampleSet(0, 0)
        For n = 3 To LAST_SAMPLE
            SampleSet(n - 3, 2) = (t0 * 1.0 + t1 * 0.5 + t2 * 0.25) / 1.75 - SampleSet(n, 0)
            t0 = t1
            t1 = t2
            t2 = SampleSet(n, 0)
        Next
        '
        ' This performs a 5-point center-average to ignore noise and determine
        ' ROI's (regions of interest) which we then use to detect R-wave maxima
        '
        For n = 2 To LAST_SAMPLE - 2
            SampleSet(n, 3) = (SampleSet(n - 2, 2) + SampleSet(n - 1, 2) + SampleSet(n, 2) + SampleSet(n + 1, 2) + SampleSet(n + 2, 2)) / 5
        Next

        ' seven-point centered average
        'For n = 3 To SampleSet.GetUpperBound(0) - 3
        'SampleSet(n, 3) = (SampleSet(n - 3, 2) + SampleSet(n - 2, 2) + SampleSet(n - 1, 2) + SampleSet(n, 2) + SampleSet(n + 1, 2) + SampleSet(n + 2, 2) + SampleSet(n + 3, 2)) / 7
        'Next

        ' nine-point centered average
        'For n = 4 To SampleSet.GetUpperBound(0) - 4
        'SampleSet(n, 3) = (SampleSet(n - 4, 2) + SampleSet(n - 3, 2) + SampleSet(n - 2, 2) + SampleSet(n - 1, 2) + SampleSet(n, 2) + SampleSet(n + 1, 2) + SampleSet(n + 2, 2) + SampleSet(n + 3, 2) + SampleSet(n + 4, 2)) / 9
        'Next

        Dim ScanPoint, PeakPoint, Rmax, Rpoint, PriorRpoint, InterbeatSamples As Integer, PeakMax As Double

        ' we begin by finding the first R-wave in the trace
        ScanPoint = 0
        PeakMax = Double.MinValue
        For n = ScanPoint To ScanPoint + LOOKAHEAD_SAMPLES - 1
            If (SampleSet(n, 3) > PeakMax) Then
                PeakMax = SampleSet(n, 3)
                PeakPoint = n
            End If
        Next

        PriorRpoint = 0 ' show that we don't yet have a previous Rmax

        ' we scan forward searching for the first ROI value that's at least 70% of the prior peak
        Do
            PeakMax = PeakMax * 0.7
            PeakPoint = 0

PeakSearch: For n = ScanPoint To ScanPoint + LOOKAHEAD_SAMPLES - 1
                If (SampleSet(n, 3) > PeakMax) Then
                    PeakMax = SampleSet(n, 3)
                    PeakPoint = n
                ElseIf (PeakPoint) Then
                    Exit For
                End If
            Next

            ' if we did not find a local qualifting peak point we scale down our search and retry
            If (PeakPoint = 0) Then
                PeakMax = PeakMax * 0.95
                GoTo PeakSearch
            End If

            ' now we locate the maximum Delta-coded R-wave within 2 samples either side of the ROI peak
            Rmax = 0
            For n = PeakPoint - 2 To PeakPoint + 2
                If SampleSet(n, 2) > Rmax Then
                    Rmax = SampleSet(n, 2)
                    Rpoint = n
                End If
            Next


            If PriorRpoint Then
                InterbeatSamples = Rpoint - PriorRpoint
                SampleSet(Rpoint, 4) = InterbeatSamples
            End If

            PriorRpoint = Rpoint

            ' bump the scanner forward 20 samples past this R-wave
            ScanPoint = Rpoint + 20
        Loop While (ScanPoint + LOOKAHEAD_SAMPLES) < LAST_SAMPLE

    End Sub
    Sub RemoveEctopicBeats(ByRef SampleSet As Array)
        ' This removes ectopic beats from the R-R interval array. It takes Array #4, as runs of interbeat intervals
        ' It takes four interbeat intervals 

        Dim Scanner, PreviousRun, Anchor1, Anchor2, Anchor3, ThisRun, Delta1, Delta2, Delta3 As Integer

        ' zero our #3 Results Array
        For n = 0 To LAST_SAMPLE
            SampleSet(n, 3) = 0
        Next

        ' find the start of the IBI data (scan from '0' to the first non)
ReDo:   Scanner = 0
        Do Until SampleSet(Scanner, 4) <> 0
            Scanner = Scanner + 1
        Loop

        'Console.WriteLine("First non-zero sample found at: " & Scanner)

        PreviousRun = 0

NextRun:

        Anchor1 = Anchor2
        Anchor2 = Anchor3
        Anchor3 = Scanner                    ' drop an anchor at the start of the run

        'Console.WriteLine("Dropping Anchor at: " & Anchor & " with value: " & AnchorVal)
        Do
            Scanner = Scanner + 1
        Loop Until (SampleSet(Scanner, 4)) Or (Scanner >= LAST_SAMPLE)

        ThisRun = Scanner - Anchor3

        If PreviousRun Then

            Delta1 = Delta2                 ' oldest delta
            Delta2 = Delta3
            Delta3 = ThisRun - PreviousRun  ' newest delta

            ' check for a posible PVC pattern in interbeat differences
            If Delta1 < 0 And Delta2 > 0 And Delta3 < 0 Then

                'Console.WriteLine("")
                'Console.WriteLine("Low/High/Low pattern found")
                'Console.WriteLine("   Synth: " & Math.Abs(Delta2 + Delta1 + Delta3) & ", vs: " & Delta2 * 0.1)

                If Math.Abs(Delta2 + Delta1 + Delta3) < (Delta2 * 0.1) Then
                    'Console.WriteLine("PVC Detected!")
                    'Console.WriteLine("   " & Math.Abs(Delta2 + Delta1 + Delta3) & " vs " & Delta2 * 0.1)
                    'Console.WriteLine("    sD1: " & Delta1 & ", D2: " & Delta2 & ", D3: " & Delta3)

                    'SampleSet(Anchor1, 3) = 825 ' show the decision points
                    'SampleSet(Anchor2, 3) = 825
                    'SampleSet(Anchor3, 3) = 825

                    SampleSet(Anchor2, 4) = 0
                    Anchor2 = Int((Anchor1 + Anchor3) / 2)
                    SampleSet(Anchor2, 4) = (Anchor2 - Anchor1)
                    SampleSet(Anchor3, 4) = (Anchor3 - Anchor2)

                    GoTo ReDo
                End If

                'Console.WriteLine("ThisRun: " & ThisRun & ", PreviousRun: " & PreviousRun & ", Delta: " & ThisRun - PreviousRun)
                'Console.WriteLine("Delta: " & ThisRun - PreviousRun)

            End If

        End If

        PreviousRun = ThisRun

        If (Scanner < LAST_SAMPLE) Then GoTo NextRun

    End Sub
    Function GetRwaveCount(ByRef SampleSet As Array) As Integer

        ' Input #4: R-wave events where value is non-zero. Has distance from previous R-wave event

        Dim ScanPoint As Integer, RwaveCount As Integer = 0

        ' scan the entire sample field locating and counting Rwave events

        For ScanPoint = 0 To LAST_SAMPLE
            If SampleSet(ScanPoint, 4) Then RwaveCount = RwaveCount + 1
        Next

        Return RwaveCount

    End Function
    Sub BuildRwaveArrays(ByRef SampleSet As Array)

        RwaveNumber = 0

        For ScanPoint = 0 To LAST_SAMPLE

            If SampleSet(ScanPoint, 4) Then
                RwaveTime(RwaveNumber) = ScanPoint
                RwaveVal(RwaveNumber) = SampleSet(ScanPoint, 4)
                RwaveNumber = RwaveNumber + 1
            End If

        Next
        RwaveNumber = RwaveNumber - 1

    End Sub
    Sub WriteRtoRintervalFile(ByVal SourceFile As String, ByVal RwaveCount As Integer)

        Dim RRintervalFile = Replace(SourceFile, ".txt", "-rr.dat")

        Dim file = My.Computer.FileSystem.OpenTextFileWriter(RRintervalFile, False, System.Text.Encoding.ASCII)
        For n = 0 To RwaveNumber
            file.WriteLine(RwaveVal(n) * 3.9)
        Next
        file.Close()

    End Sub
    Sub WriteHeartWaveFile(ByVal SourceFile As String, ByVal RwaveCount As Integer)

        Dim RRintervalFile = Replace(SourceFile, ".txt", "-wave.dat")
        Dim file = My.Computer.FileSystem.OpenTextFileWriter(RRintervalFile, False, System.Text.Encoding.ASCII)
        For n = 0 To RwaveNumber
            Dim val = RwaveVal(n)
            For i = 0 To val
                file.WriteLine(val)
            Next
        Next
        file.Close()

    End Sub
    Sub BuildRmsTimeline()

        'Buterworth Low-Pass 100hz/ 5hz:  GAIN:  7.313751515 / yv0: 0.726542528
        '                         / 1hz:        32.82051595  /      0.9390625058
        '                          10hz:         4.077683537 /      0.5095254495
        '                           3hz:        11.57889499  /      0.8272719460
        '                           4hz:         8.915815088 /      0.7756795110
        '                         0.5hz:        64.65674116  /      0.9690674172
        '                         0.1hz:       319.308839    /      0.9937364715
        Dim xv0, xv1, yv0, yv1, Sum As Double, polarity As Boolean

        For n = 0 To RwaveNumber
            RmsVal(n) = 0
        Next

        xv1 = RwaveVal(0)
        RmsMax = Double.MinValue

        For n = 1 To RwaveNumber
            xv0 = xv1
            xv1 = RwaveVal(n) / 64.65674116
            yv0 = yv1
            yv1 = (xv0 + xv1) + (0.9690674172 * yv0)

            'Console.WriteLine("In: " & RwaveVal(n) & ", Out: " & yv1)

            If (polarity Xor (RwaveVal(n) > yv1)) Then
                RmsVal(n) = Sum
                If Sum > RmsMax Then
                    RmsMax = Sum
                End If
                polarity = (RwaveVal(n) > yv1)
                Sum = 0
            End If
            Sum = Sum + (Math.Abs(RwaveVal(n) - yv1) * (RwaveTime(n) - RwaveTime(n - 1)))

        Next
        RmsVal(RwaveNumber) = Sum

        ' now we rescale the RmsVal array to 2*YSCALE
        Dim RmsScale = 2 * YSCALE / RmsMax
        For n = 0 To RwaveNumber
            RmsVal(n) = RmsVal(n) * RmsScale - YSCALE
        Next

    End Sub
    Sub AverageAndInvertRwave()

        Dim SkipCount As Integer = Int(RwaveCount * 0.05)
        Dim Sum As Integer = 0

        For i = SkipCount To RwaveCount - SkipCount
            Sum = Sum + RwaveVal(i)
        Next
        Sum = Sum / (RwaveCount - 2 * SkipCount)

        For i = 0 To RwaveCount - 1
            RwaveVal(i) = Sum - RwaveVal(i)
        Next

    End Sub
    Sub RebaseAndInvertRwaves()
        ' This brings the r-wave intervals to a flat baseline. Lowess smoothing
        ' is used to create a phase-neutral tracking curve from which individual
        ' r-wave intervals are subtracted.

        Lowess2(RwaveTime, RwaveVal, RwaveVals, 31)

        For i = 0 To RwaveCount - 1
            RwaveVal(i) = RwaveVals(i) - RwaveVal(i)
        Next

    End Sub
    Sub FindHrvPeaks()
        ' This scans the <RwaveTime|Rwave Val> array pair to alternatively
        ' locate the maximum and minimum heart rate value. When found, the
        ' <Time|Val> are placed into the <PeakTimes|PeakVals> array pair.

        Dim LocalMax, CurrentVal As Double
        Dim PeakIndex As Integer, CurrentIndex As Integer = 0
        Dim PeakTimes, PeakVals As New Collection

        ' search for positive maximum before next zero-crossing
PosPeak: LocalMax = Double.MinValue
        Do
            CurrentVal = RwaveVal(CurrentIndex)
            If CurrentVal > LocalMax Then
                LocalMax = CurrentVal
                PeakIndex = RwaveTime(CurrentIndex)
            End If
            CurrentIndex = CurrentIndex + 1
            If CurrentIndex > (RwaveCount - 1) Then GoTo BuildArrays
        Loop Until CurrentVal < 0

        PeakTimes.Add(PeakIndex)
        PeakVals.Add(LocalMax)

        ' search for negative maximum before next zero-crossing
NegPeak: LocalMax = Double.MaxValue
        Do
            CurrentVal = RwaveVal(CurrentIndex)
            If CurrentVal < LocalMax Then
                LocalMax = CurrentVal
                PeakIndex = RwaveTime(CurrentIndex)
            End If
            CurrentIndex = CurrentIndex + 1
            If CurrentIndex > (RwaveCount - 1) Then GoTo BuildArrays
        Loop Until CurrentVal > 0

        PeakTimes.Add(PeakIndex)
        PeakVals.Add(LocalMax)

        GoTo PosPeak

        ' having built adhoc collections of the times & vals, we
        ' get the count, resize the permanent arrays, enumerate the
        ' collections into the arrays, and discard the collections

BuildArrays:

        Array.Resize(PeakTime, PeakTimes.Count)
        Array.Resize(PeakVal, PeakVals.Count)

        Dim TimesEnum As IEnumerator = PeakTimes.GetEnumerator()
        Dim ValsEnum As IEnumerator = PeakVals.GetEnumerator()

        CurrentIndex = 0
        While TimesEnum.MoveNext() And ValsEnum.MoveNext()
            PeakTime(CurrentIndex) = TimesEnum.Current
            PeakVal(CurrentIndex) = ValsEnum.Current
            CurrentIndex = CurrentIndex + 1
        End While
        LastPeak = CurrentIndex - 1

        Console.WriteLine("HRV Peaks Found: " & CurrentIndex)

    End Sub
    Sub MeasurePeakToPeak()

        Dim RmsScale As Double

        Array.Resize(RmsVal, LastPeak)
        Array.Resize(RmsVals, LastPeak)

        RmsMax = Double.MinValue
        RmsMin = Double.MaxValue

        For n = 0 To LastPeak - 1
            RmsVal(n) = Math.Abs(PeakVal(n) - PeakVal(n + 1))
            If RmsVal(n) > RmsMax Then RmsMax = RmsVal(n)
            If RmsVal(n) < RmsMin Then RmsMin = RmsVal(n)
        Next

        ' shooth RmsVal[] into RmsVals[]
        ' Lowess2(PeakTime, RmsVal, RmsVals, 23)
        Lowess2(PeakTime, RmsVal, RmsVals, 21)

        RmsScale = 2 * YSCALE / (RmsMax - RmsMin)

        ' now we find the location of the largest RmsVal[]
        RmsMax = Double.MinValue

        For n = 0 To LastPeak - 1
            RmsVal(n) = (RmsVals(n) - RmsMin) * RmsScale - YSCALE
            If RmsVal(n) > RmsMax Then
                RmsMax = RmsVal(n)
                PeakPoint = PeakTime(n)
            End If
        Next

    End Sub
    Sub RescaleBR(ByRef SampleSet As Array)

        Dim BR_Max = Double.MinValue, BR_Min = Double.MaxValue, BR_Scale As Double

        For n = 0 To LAST_SAMPLE
            If SampleSet(n, 1) > BR_Max Then BR_Max = SampleSet(n, 1)
            If SampleSet(n, 1) < BR_Min Then BR_Min = SampleSet(n, 1)
        Next

        If BR_Max < -BR_Min Then BR_Max = -BR_Min

        BR_Scale = YSCALE / BR_Max * 0.98

        For n = 0 To LAST_SAMPLE
            SampleSet(n, 1) = SampleSet(n, 1) * BR_Scale
        Next

    End Sub
    Sub RescaleHR()

        Dim HR_Max = Double.MinValue, HR_Min = Double.MaxValue, HR_Scale As Double

        For n = 0 To RwaveCount - 1
            If RwaveVal(n) > HR_Max Then HR_Max = RwaveVal(n)
            If RwaveVal(n) < HR_Min Then HR_Min = RwaveVal(n)
        Next

        If HR_Max < -HR_Min Then HR_Max = -HR_Min

        HR_Scale = YSCALE / HR_Max * 0.98

        For n = 0 To RwaveCount - 1
            RwaveVal(n) = RwaveVal(n) * HR_Scale
        Next

    End Sub
    Function GetError(ByVal Phase As Double, ByVal Omega As Double, ByVal Amplitude As Double, ByVal Offset As Double, ByVal FirstSample As Integer, ByVal LastSample As Integer, ByRef SampleSet As Array)

        GetError = 0.0
        For n = FirstSample To LastSample
            GetError = GetError + Math.Abs(Amplitude * Math.Cos(Phase) + Offset - SampleSet(n, 1))
            Phase = Phase + Omega               ' advance our osccillator
        Next n

    End Function
    Sub SineWaveFit(ByRef SampleSet As Array)

        Dim INITIAL_BREATHS_PER_MIN = 5.5   ' our oscillator's initial frequency

        ' set the starting point for our sine fit
        Dim FirstSample = PeakPoint - (SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2)
        Do While FirstSample < 0
            FirstSample = FirstSample + SAMPLES_PER_SECOND
        Loop

        ' set the ending point for our sine fit
        Dim LastSample = PeakPoint + (SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2)
        Do While LastSample > LAST_SAMPLE
            LastSample = LastSample - SAMPLES_PER_SECOND
        Loop

        ' we begin by estimating the amplitude and offset with a min & max
        Dim Max = Double.MinValue, Min = Double.MaxValue
        For n = FirstSample To LastSample
            If SampleSet(n, 1) > Max Then Max = SampleSet(n, 1)
            If SampleSet(n, 1) < Min Then Min = SampleSet(n, 1)
        Next

        Dim CosScale = (Max - Min) / 2
        Dim CosOffset = (Max + Min) / 2
        Dim Pi = Math.PI            ' get Pi for our use.
        Dim Omega = 2 * Pi / 60 * INITIAL_BREATHS_PER_MIN / SAMPLES_PER_SECOND
        Dim Phase = 0.0

SearchPhase:

        Dim Corrections = 0

        Console.Write("Sliding Phase: ")

        Dim LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

        Dim PhaseStep = Pi / 100
        If LastError < GetError(Phase + PhaseStep, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet) Then
            PhaseStep = -PhaseStep
            Console.WriteLine("Earlier")
        Else
            Console.WriteLine("Later")
        End If

        For i = 0 To 200
            Phase = Phase + PhaseStep
            Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
            If LastError < ThisError Then Exit For
            LastError = ThisError
            Console.WriteLine("    Error: {0:0}", ThisError)
            Corrections = Corrections + 1
        Next i
        Phase = Phase - PhaseStep

        ' Adjust Frequency

        LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

        Dim OmegaStep = 1.001
        If LastError < GetError(Phase, Omega * OmegaStep, CosScale, CosOffset, FirstSample, LastSample, SampleSet) Then
            OmegaStep = 1 / OmegaStep
            Console.WriteLine("Increasing Frequency")
        Else
            Console.WriteLine("Decreasing Frequency")
        End If

        For i = 0 To 200
            Omega = Omega * OmegaStep
            Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
            If LastError < ThisError Then Exit For
            LastError = ThisError
            Console.WriteLine("    Error: {0:0}", ThisError)
            Corrections = Corrections + 1
        Next i
        Omega = Omega / OmegaStep

        ' Adjust DC Offset

        LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

        Dim OffsetStep = 1
        If LastError < GetError(Phase, Omega, CosScale, CosOffset + OffsetStep, FirstSample, LastSample, SampleSet) Then
            OffsetStep = -1
            Console.WriteLine("Shifting Negative")
        Else
            Console.WriteLine("Shifting Positive")
        End If

        For i = 0 To 200
            CosOffset = CosOffset + OffsetStep
            Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
            If LastError < ThisError Then Exit For
            LastError = ThisError
            Console.WriteLine("    Error: {0:0}", ThisError)
            Corrections = Corrections + 1
        Next i
        CosOffset = CosOffset - OffsetStep

        ' Adjusting Amplitude

        LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

        Dim AmplitudeScale = 1.005
        If LastError < GetError(Phase, Omega, CosScale * AmplitudeScale, CosOffset + OffsetStep, FirstSample, LastSample, SampleSet) Then
            AmplitudeScale = 1 / AmplitudeScale
            Console.WriteLine("Decreasing Amplitude")
        Else
            Console.WriteLine("Increasing Amplitude")
        End If

        For i = 0 To 200
            CosScale = CosScale * AmplitudeScale
            Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
            If LastError < ThisError Then Exit For
            LastError = ThisError
            Console.WriteLine("    Error: {0:0}", ThisError)
            Corrections = Corrections + 1
        Next i
        CosScale = CosScale / AmplitudeScale


        If Corrections Then GoTo SearchPhase

Show:

        For n = FirstSample To LastSample
            SampleSet(n, 2) = CosScale * Math.Cos(Phase)
            Phase = Phase + Omega               ' advance our osccillator
        Next n

        ResonanceBpm = Omega / 2 / Pi * 60 * SAMPLES_PER_SECOND
        Console.WriteLine("Calculated actual breaths per minute: {0:0.00}", ResonanceBpm)

    End Sub
End Module