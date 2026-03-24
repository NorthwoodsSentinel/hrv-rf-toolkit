Public Class Processing

    Private Sub Processing_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load

		Me.Show()
		Dim FileToProcess As String = ""

		' FileToProcess = "C:\Users\SMG\Desktop\HRV\GS72Sliding-30andREAF.txt"
        ' FileToProcess = "C:\Users\SMG\Documents\Visual Studio 2008\Projects\Nexus\Nexus\Alyssa-Short.txt"
        ' FileToProcess = "C:\Users\SMG\Documents\Visual Studio 2008\Projects\Nexus\Nexus\Alyssa.txt"

		If (FileToProcess <> "") Then
			Processfile(FileToProcess)
		Else
			Dim CommandLineArguments As String() = Environment.GetCommandLineArgs()
			For i = 0 To CommandLineArguments.GetUpperBound(0)
				FileToProcess = CommandLineArguments(i)
				If FileToProcess.Contains(".txt") Then
					Processfile(FileToProcess)
					Exit Sub
				End If
			Next
			If CommandLineArguments.GetUpperBound(0) > 0 Then MsgBox("That was not a valid Nexus export file.")
		End If
	End Sub
    Private Sub Processing_DragDrop(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles DropInstruction.DragDrop

		Dim files() As String = e.Data.GetData(DataFormats.FileDrop)
		If files.Length = 1 Then
			If files(0).Contains(".txt") Then
				Processfile(files(0))
			Else
				MsgBox("That was not a valid Nexus export file.")
			End If
		End If
	End Sub
    Private Sub Processing_DragEnter(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles DropInstruction.DragEnter

        If e.Data.GetDataPresent(DataFormats.FileDrop) Then
            e.Effect = DragDropEffects.Copy
        End If

	End Sub
	Public Sub Processfile(ByVal FileToProcess As String)

		' capture the state of the SHIFT keys at program startup
		BreathOnly = My.Computer.Keyboard.ShiftKeyDown

		If (BreathOnly) Then
			ProgressBar1.Visible = False
			ProgressBar2.Visible = False
			ProgressBar3.Visible = False
			ProgressBar4.Visible = False
			ProgressBar5.Visible = False

			Label5.Visible = False
			Label6.Visible = False
			Label7.Visible = False
			Label8.Visible = False
			Label9.Visible = False
			Label10.Visible = False
			Label11.Visible = False
			Label12.Visible = False

			Label21.Visible = False
			Label22.Visible = False
			Label23.Visible = False
			Label24.Visible = False
			Label25.Visible = False
		End If

		DropInstruction.Visible = False

		Dim NameComponents = Split(FileToProcess, "\")	' split the filename at the \'s
		Dim NameComponent = NameComponents(UBound(NameComponents))
		' get the last of the components and remove the '.txt' filename extension
		NameProcessed = Strings.Left(NameComponent, Len(NameComponent) - 4)
		Me.Text = " Processing File:  " & NameProcessed	' show the filename we're processing.
		Me.Cursor = Cursors.WaitCursor
		Application.DoEvents()

		ProcessData(FileToProcess)

		If FileProcessed Then
			' we've finished our processing...
			FirstSample = 0						' setup our initial display range
			LastSample = LAST_SAMPLE			' we show =ALL= of the data

			' now we switch screens to handoff from the progress monitor to the results display
			HRV_Display.Show()					' show the results display
		End If
		Me.Close()							' and terminate ourself
	End Sub
	Private Sub Processing_FormClosing(ByVal sender As Object, ByVal e As FormClosingEventArgs) Handles Me.FormClosing
		If Not FileProcessed Then End
	End Sub
End Class