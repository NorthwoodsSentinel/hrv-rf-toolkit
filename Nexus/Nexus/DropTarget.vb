Public Class DropTarget

    Dim OurSampleSet As Array, FirstSample, LastSample As Integer, DataFile As String
    'Dim Anote As DataVisualization.Charting.TextAnnotation
    'Dim Afont = New Font("Verdana", 14)

    Private Sub DropTarget_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
		' DropTarget_Load is our starting point...

		Dim Width As Integer = Screen.PrimaryScreen.Bounds.Width
        Dim Height As Integer = Screen.PrimaryScreen.Bounds.Height

        Me.Size = New Size(4 * Width / 5, 2 * Height / 5)
        Me.Left = (Width - Me.Width) / 2
        Me.Top = (Height - Me.Height) / 2

        Me.AllowDrop = True
        Me.BackColor = Color.White
        ChartSetup()
        'Processfile("C:\Users\SMG\Desktop\HRV\lrf.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\smg1.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\smg1-trunc.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\15 decel.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\smg 3min steps.txt")
		'Processfile("C:\Users\SMG\Desktop\HRV\lrf 3min steps.txt")

		'Processfile("C:\Users\SMG\Desktop\HRV\LRF 063018.txt")
		Processfile("C:\Users\SMG\Desktop\HRV\Alyssa.txt")
		'Processfile("Alyssa.txt")

        'Processfile("lrf 3min steps.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\lrf 10 breath steps.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\lrf 3min steps tail.txt")
        'Processfile("C:\Users\SMG\Desktop\HRV\Robert 5 breaths 7 to 4.txt")

        '        Dim SampleSet(2, 2) As Single
        '        Display(SampleSet)
        '        Chart.Visible = True
        '        DropInstruction.Visible = False

    End Sub
    Private Sub DropTarget_DragDrop(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles Me.DragDrop

        Dim files() As String = e.Data.GetData(DataFormats.FileDrop)
        If files.Length = 1 Then

            Console.WriteLine("File" & files(0))
            Processfile(files(0))

        End If

    End Sub
    Private Sub DropTarget_DragEnter(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles Me.DragEnter

        If e.Data.GetDataPresent(DataFormats.FileDrop) Then
            e.Effect = DragDropEffects.Copy
        End If

    End Sub
    Private Sub DropTarget_Resize(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Resize

        Chart.Left = 25
        Chart.Top = MenuStrip.Height + 25
        Chart.Size = New Size(Me.Width - 68, Me.Height - (StatusStrip.Height + MenuStrip.Height + HScrollBar.Height + 65))

    End Sub
    Private Sub PrintToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles PrintToolStripMenuItem.Click

        Dim pd As System.Drawing.Printing.PrintDocument = Chart.Printing.PrintDocument
        pd.DefaultPageSettings.Landscape = True
        Dim margins As New System.Drawing.Printing.Margins(0, 0, 0, 0)
        pd.DefaultPageSettings.Margins = margins

        Chart.Printing.Print(True)

    End Sub
    Sub PrintPreview(ByVal pd As System.Drawing.Printing.PrintDocument)

        ' Declare the dialog.
        Dim ppd As PrintPreviewDialog = New PrintPreviewDialog

        'Set the size, location, and name.
        ppd.ClientSize = New System.Drawing.Size(800, 600)
        ppd.Location = New System.Drawing.Point(0, 0)
        ppd.UseAntiAlias = True
        ppd.Document = pd 'Chart.Printing.PrintDocument
        ppd.ShowDialog()

    End Sub
    Public Sub Processfile(ByRef FileToProcess As String)

		DropInstruction.Text = "Processing Data..."
		DropInstruction.Visible = True
		Chart.Visible = False
		Me.Text = "<<<<< Processing Nexus Data >>>>>"
		Me.Cursor = Cursors.WaitCursor
		Application.DoEvents()
		OurSampleSet = ProcessingCode.ProcessData(FileToProcess)

		Application.DoEvents()

		FirstSample = 256			   ' discard the first and
		LastSample = LAST_SAMPLE - 256	' last second of captured data

		HScrollBar.Minimum = FirstSample
		HScrollBar.Maximum = LastSample
		HScrollBar.LargeChange = HScrollBar.Maximum

		Display()
		Application.DoEvents()

		Chart.Visible = True
		DropInstruction.Visible = False
		Me.Text = "HRVisualizer Processing Complete"
		Me.Cursor = Cursors.Arrow

    End Sub
    Public Sub SaveProcessedData()

        'If DataFile = "C:\Users\SMG\Desktop\HRV\15 decel.dat" Then Exit Sub
        'If DataFile = "C:\Users\SMG\Desktop\HRV\lrf 3min steps tail.dat" Then Exit Sub

        ' Dim file As System.IO.StreamWriter
        Dim file = My.Computer.FileSystem.OpenTextFileWriter(DataFile, False)
        For n = 0 To SampleCount - 1
            file.WriteLine(OurSampleSet(n, 2) & "," & OurSampleSet(n, 1) & "," & OurSampleSet(n, 0))
        Next
        file.Close()

    End Sub
    Public Sub ChartSetup()

        Dim area = Chart.ChartAreas(0)

        area.AxisX.LineWidth = 2
        area.AxisX.ScrollBar.Enabled = False
        area.AxisX.MajorTickMark.Enabled = False
        area.AxisX.MinorTickMark.Enabled = False
        area.AxisX.IsStartedFromZero = False

        area.AxisX.Title = "Breath Cycle and Heart Rate Variability"
        area.AxisX.LabelStyle.Enabled = True
        area.AxisX.TitleFont = New System.Drawing.Font("Microsoft Sans Serif", 20)
        area.AxisX.TitleForeColor = Color.Green

        'area.AxisX.LabelStyle.Interval = 2000
        'area.AxisX.CustomLabels.
        'area.AxisX.LabelStyle.Enabled = False
        area.AxisX.Interval = 1

        area.AxisY.LineWidth = 2
        area.AxisY.ScrollBar.Enabled = False
        area.AxisY.LabelStyle.Enabled = False
        area.AxisY.MajorTickMark.Enabled = False
        area.AxisY.MinorTickMark.Enabled = False
        area.AxisY.IsStartedFromZero = False
        area.AxisY.Maximum = YSCALE * 1.0
        area.AxisY.Minimum = -YSCALE * 1.0

        area.Position.X = 0
        area.Position.Y = 0
        area.Position.Width = 100
        area.Position.Height = 100

        'area.AxisY2.Enabled = True
        'area.AxisY2.LabelStyle.Enabled = False
        'area.AxisY2.MajorTickMark.Enabled = False
        'area.AxisY2.LineWidth = 3

        'Chart.ChartAreas(0).AxisX.LineWidth = 2
        'Chart.ChartAreas(0).AxisY.LineWidth = 2
        'Chart.ChartAreas(0).AxisX.LabelStyle.Enabled = False
        'Chart.ChartAreas(0).AxisY.LabelStyle.Enabled = False
        'Chart.ChartAreas(0).AxisX.MajorGrid.Enabled = False
        'Chart.ChartAreas(0).AxisY.MajorGrid.Enabled = False
        'Chart.ChartAreas(0).AxisX.MinorGrid.Enabled = False
        'Chart.ChartAreas(0).AxisY.MinorGrid.Enabled = False
        'Chart.ChartAreas(0).AxisX.MajorTickMark.Enabled = False
        'Chart.ChartAreas(0).AxisY.MajorTickMark.Enabled = False
        'Chart.ChartAreas(0).AxisX.MinorTickMark.Enabled = False
        'Chart.ChartAreas(0).AxisY.MinorTickMark.Enabled = False

        'area.AxisX.Minimum = 0
        'area.AxisX.Maximum = 15
        'area.CursorX.AutoScroll = True

    End Sub
    Public Sub Display() ' ByRef SampleSet As Array)

		Dim area = Chart.ChartAreas(0)

        area.AxisX.Minimum = FirstSample
        area.AxisX.Maximum = LastSample
        area.AxisX.Interval = LastSample - FirstSample
        area.AxisX.IntervalOffset = 0
        area.AxisX.LabelStyle.IsEndLabelVisible = False

        area.AxisY.Interval = 2 * YSCALE

        Chart.Series.SuspendUpdates()
        Chart.Series.Clear()
        Chart.Annotations.Clear()
        Chart.AntiAliasing = True


		Dim SINE_FIT_series = Chart.Series.Add("SineFit Series")
		With SINE_FIT_series
			.Color = Color.LightGray
			.ChartType = DataVisualization.Charting.SeriesChartType.Line
			.BorderWidth = 10 ' THICK_TRACE
		End With

		Dim TL_series = Chart.Series.Add("Variation Series")
		With TL_series
			.Color = Color.LawnGreen
			.ChartType = DataVisualization.Charting.SeriesChartType.Line
			.BorderWidth = THICK_TRACE
		End With

		Dim HR_series = Chart.Series.Add("Heart Rate Series")
        With HR_series
            .Color = Color.Red
            'BB_series.Color = Color.DarkSlateGray
            .ChartType = DataVisualization.Charting.SeriesChartType.Line
            .BorderWidth = TRACE_WIDTH
        End With

		Dim BR_series = Chart.Series.Add("Breathing Series")
        With BR_series
            .Color = Color.Blue
            '.Color = Color.Black
            .ChartType = DataVisualization.Charting.SeriesChartType.Line
            .BorderWidth = TRACE_WIDTH
        End With

		Dim PEAK_POINT_series = Chart.Series.Add("TICK Series")
		With PEAK_POINT_series
			.Color = Color.Black
			.ChartType = DataVisualization.Charting.SeriesChartType.Line
			.BorderDashStyle = DataVisualization.Charting.ChartDashStyle.Dash
			.BorderWidth = 3	' THICK_TRACE
		End With


        '======================================================================
        Dim StepSize = Int((LastSample - FirstSample) / Chart.Width)
        If StepSize < 1 Then StepSize = 1
        If LastSample > SampleCount - 1 Then LastSample = SampleCount - 1
        For n = FirstSample To LastSample Step StepSize
			BR_series.Points.AddXY(n, OurSampleSet(n, 1))	' breathing
		Next


		'======================================================================
		For n = 0 To RwaveCount - 1
			If RwaveTime(n) >= FirstSample And RwaveTime(n) <= LastSample Then
				HR_series.Points.AddXY(RwaveTime(n), RwaveVal(n))
			End If
		Next


		'======================================================================
		'For i = 0 To LastBreathEvent
		'If BreathEventTime(i) >= FirstSample And BreathEventTime(i) <= LastSample Then

		'MARKER_series.Points.AddXY(BreathEventTime(i), BreathEventVal(i))
		'MARKER_series.Points.AddXY(BreathEventTime(i), BreathEventPeriods(i))

		'End If
		'Next


		'======================================================================
		For i = 0 To LastPeak - 1
			If PeakTime(i) >= FirstSample And PeakTime(i) <= LastSample Then
				TL_series.Points.AddXY(PeakTime(i), RmsVal(i))
			End If
		Next


		'======================================================================
		PEAK_POINT_series.Points.AddXY(PeakPoint, -YSCALE)
		PEAK_POINT_series.Points.AddXY(PeakPoint, YSCALE * 0.75)


		'======================================================================
		Dim FirstSine = PeakPoint - SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2
		Dim LastSine = PeakPoint + SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2
		For n = FirstSine To LastSine
			SINE_FIT_series.Points.AddXY(n, OurSampleSet(n, 2))
		Next


		Dim CC_series = Chart.Series.Add("Breathing Rate Series")
		With CC_series
			.Color = Color.Blue
			'.IsVisibleInLegend = False
			.ChartType = DataVisualization.Charting.SeriesChartType.Point
			.MarkerStyle = DataVisualization.Charting.MarkerStyle.Triangle
			.MarkerSize = 0
			'CC_series.Font = New System.Drawing.Font("Microsoft Sans Serif", 20)
			'CC_series.Font = New System.Drawing.Font("Microsoft Sans Serif", 30)
		End With


		'======================================================================
		Dim Afont = New System.Drawing.Font("Verdana", 14)

		'For n = FirstSample To LastSample
		'If (OurSampleSet(n, 0) <> 0) Then

		Dim Pt = CC_series.Points.AddXY(PeakPoint, YSCALE)

		Dim Anote = New DataVisualization.Charting.TextAnnotation
		Anote.Text = String.Format("{0:F2}", ResonanceBpm)
		Anote.Font = Afont
		Anote.AnchorDataPoint = CC_series.Points(Pt)
		Chart.Annotations.Add(Anote)

		'End If
		'Next

		Chart.Series.ResumeUpdates()
		Chart.Refresh()

	End Sub

    Private Sub Chart_Resize(ByVal sender As Object, ByVal e As System.EventArgs) Handles Chart.Resize

        If (FileProcessed) Then Display()

    End Sub

    'Public Sub UpdateChart(ByRef SampleSet As Array)

    'Chart.Series.SuspendUpdates()





    'Chart.Series.ResumeUpdates()


    'Dim ChartSize As Size = Chart.Size

    'w = Chart.Width

    'Chart.Top = MenuStrip.Height + 25
    'Chart.Size = New Size(Me.Width - 50, Me.Height - (StatusStrip.Height + MenuStrip.Height + 70))




    'End Sub

    Private Sub Chart_MouseWheel(ByVal sender As Object, ByVal e As MouseEventArgs) Handles Me.MouseWheel

        Dim Clicks = e.Delta, Span, Center, Delta As Integer

        Span = LastSample - FirstSample + 1

        If Clicks < 0 Then
            Span = Span * 0.9
            If Span < 100 Then Span = 100
        Else
            Span = Span / 0.9
            If Span > SampleCount Then Span = SampleCount - 512
        End If

        Center = Int((LastSample + FirstSample) / 2)
        FirstSample = Int(Center - Span / 2)
        LastSample = Int(Center + Span / 2)

        If FirstSample < 256 Then
            Delta = 256 - FirstSample
            FirstSample = FirstSample + Delta
            LastSample = LastSample + Delta
        End If

        If LastSample > (SampleCount - 256) Then
            Delta = LastSample - (SampleCount - 256)
            FirstSample = FirstSample - Delta
            LastSample = LastSample - Delta
        End If

        If FirstSample < 256 Then FirstSample = 256
        If LastSample > (SampleCount - 257) Then LastSample = SampleCount - 257

        HScrollBar.LargeChange = LastSample - FirstSample
        HScrollBar.Value = FirstSample
        HScrollBar.SmallChange = Span / 20

        Display()

    End Sub


    'Private Sub Chart_MouseEnter(ByVal sender As Object, ByVal e As System.EventArgs) Handles Chart.MouseEnter

    'Me.Focus()

    'End Sub

    'Private Sub Chart_MouseLeave(ByVal sender As Object, ByVal e As System.EventArgs) Handles Chart.MouseLeave

    'Me.Parent.Focus()

    'End Sub

    Private Sub HScrollBar_ValueChanged(ByVal sender As System.Object, ByVal e As EventArgs) Handles HScrollBar.ValueChanged

        Dim Span = LastSample - FirstSample + 1

        FirstSample = HScrollBar.Value
        LastSample = FirstSample + Span
        Display()

    End Sub

    Private Sub DropInstruction_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles DropInstruction.Click

    End Sub
End Class
