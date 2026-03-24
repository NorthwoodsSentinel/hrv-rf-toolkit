<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Processing
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
		Me.DropInstruction = New System.Windows.Forms.Label
		Me.Label1 = New System.Windows.Forms.Label
		Me.ProgressBar4 = New System.Windows.Forms.ProgressBar
		Me.Label2 = New System.Windows.Forms.Label
		Me.Label3 = New System.Windows.Forms.Label
		Me.Label4 = New System.Windows.Forms.Label
		Me.Label5 = New System.Windows.Forms.Label
		Me.Label6 = New System.Windows.Forms.Label
		Me.Label7 = New System.Windows.Forms.Label
		Me.Label8 = New System.Windows.Forms.Label
		Me.ProgressBar2 = New System.Windows.Forms.ProgressBar
		Me.Label9 = New System.Windows.Forms.Label
		Me.ProgressBar5 = New System.Windows.Forms.ProgressBar
		Me.Label10 = New System.Windows.Forms.Label
		Me.Label11 = New System.Windows.Forms.Label
		Me.Label12 = New System.Windows.Forms.Label
		Me.Label13 = New System.Windows.Forms.Label
		Me.Label14 = New System.Windows.Forms.Label
		Me.Label15 = New System.Windows.Forms.Label
		Me.Label16 = New System.Windows.Forms.Label
		Me.Label18 = New System.Windows.Forms.Label
		Me.Label19 = New System.Windows.Forms.Label
		Me.Label20 = New System.Windows.Forms.Label
		Me.Label21 = New System.Windows.Forms.Label
		Me.Label22 = New System.Windows.Forms.Label
		Me.Label24 = New System.Windows.Forms.Label
		Me.Label23 = New System.Windows.Forms.Label
		Me.Label25 = New System.Windows.Forms.Label
		Me.ProgressBar1 = New System.Windows.Forms.ProgressBar
		Me.ProgressBar3 = New System.Windows.Forms.ProgressBar
		Me.SuspendLayout()
		'
		'DropInstruction
		'
		Me.DropInstruction.AllowDrop = True
		Me.DropInstruction.BackColor = System.Drawing.Color.Transparent
		Me.DropInstruction.Cursor = System.Windows.Forms.Cursors.Arrow
		Me.DropInstruction.Dock = System.Windows.Forms.DockStyle.Fill
		Me.DropInstruction.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.DropInstruction.ForeColor = System.Drawing.Color.FromArgb(CType(CType(0, Byte), Integer), CType(CType(0, Byte), Integer), CType(CType(192, Byte), Integer))
		Me.DropInstruction.Location = New System.Drawing.Point(0, 0)
		Me.DropInstruction.Margin = New System.Windows.Forms.Padding(2, 0, 2, 0)
		Me.DropInstruction.Name = "DropInstruction"
		Me.DropInstruction.Size = New System.Drawing.Size(304, 265)
		Me.DropInstruction.TabIndex = 2
		Me.DropInstruction.Text = "Drop Nexus data file here" & Global.Microsoft.VisualBasic.ChrW(13) & Global.Microsoft.VisualBasic.ChrW(10) & "to process and display..."
		Me.DropInstruction.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label1
		'
		Me.Label1.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label1.Location = New System.Drawing.Point(13, 10)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(165, 20)
		Me.Label1.TabIndex = 3
		Me.Label1.Text = "File sample count:"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ProgressBar4
		'
		Me.ProgressBar4.Location = New System.Drawing.Point(184, 155)
		Me.ProgressBar4.Name = "ProgressBar4"
		Me.ProgressBar4.Size = New System.Drawing.Size(106, 15)
		Me.ProgressBar4.TabIndex = 4
		'
		'Label2
		'
		Me.Label2.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label2.Location = New System.Drawing.Point(13, 30)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(165, 20)
		Me.Label2.TabIndex = 5
		Me.Label2.Text = "Total recording seconds:"
		Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label3
		'
		Me.Label3.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label3.Location = New System.Drawing.Point(13, 50)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(165, 20)
		Me.Label3.TabIndex = 6
		Me.Label3.Text = "Minutes:"
		Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label4
		'
		Me.Label4.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label4.Location = New System.Drawing.Point(13, 70)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(165, 20)
		Me.Label4.TabIndex = 7
		Me.Label4.Text = "Trimmed sample count:"
		Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label5
		'
		Me.Label5.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label5.Location = New System.Drawing.Point(13, 90)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(165, 20)
		Me.Label5.TabIndex = 8
		Me.Label5.Text = "Processing raw ECG data:"
		Me.Label5.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label6
		'
		Me.Label6.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label6.Location = New System.Drawing.Point(13, 110)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(165, 20)
		Me.Label6.TabIndex = 9
		Me.Label6.Text = "Removing ectopic beats:"
		Me.Label6.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label7
		'
		Me.Label7.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label7.Location = New System.Drawing.Point(13, 130)
		Me.Label7.Name = "Label7"
		Me.Label7.Size = New System.Drawing.Size(165, 20)
		Me.Label7.TabIndex = 10
		Me.Label7.Text = "R-waves found:"
		Me.Label7.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label8
		'
		Me.Label8.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label8.Location = New System.Drawing.Point(13, 150)
		Me.Label8.Name = "Label8"
		Me.Label8.Size = New System.Drawing.Size(165, 20)
		Me.Label8.TabIndex = 11
		Me.Label8.Text = "Aligning R-R interval data:"
		Me.Label8.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ProgressBar2
		'
		Me.ProgressBar2.Location = New System.Drawing.Point(184, 95)
		Me.ProgressBar2.Name = "ProgressBar2"
		Me.ProgressBar2.Size = New System.Drawing.Size(106, 15)
		Me.ProgressBar2.TabIndex = 12
		'
		'Label9
		'
		Me.Label9.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label9.Location = New System.Drawing.Point(13, 170)
		Me.Label9.Name = "Label9"
		Me.Label9.Size = New System.Drawing.Size(165, 20)
		Me.Label9.TabIndex = 14
		Me.Label9.Text = "Minima && maxima found:"
		Me.Label9.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ProgressBar5
		'
		Me.ProgressBar5.Location = New System.Drawing.Point(184, 195)
		Me.ProgressBar5.Name = "ProgressBar5"
		Me.ProgressBar5.Size = New System.Drawing.Size(106, 15)
		Me.ProgressBar5.TabIndex = 13
		'
		'Label10
		'
		Me.Label10.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label10.Location = New System.Drawing.Point(13, 190)
		Me.Label10.Name = "Label10"
		Me.Label10.Size = New System.Drawing.Size(165, 20)
		Me.Label10.TabIndex = 16
		Me.Label10.Text = "Locating min/max rates:"
		Me.Label10.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label11
		'
		Me.Label11.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label11.Location = New System.Drawing.Point(13, 210)
		Me.Label11.Name = "Label11"
		Me.Label11.Size = New System.Drawing.Size(165, 20)
		Me.Label11.TabIndex = 17
		Me.Label11.Text = "Peak excursion at sample:"
		Me.Label11.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label12
		'
		Me.Label12.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label12.Location = New System.Drawing.Point(12, 230)
		Me.Label12.Name = "Label12"
		Me.Label12.Size = New System.Drawing.Size(165, 20)
		Me.Label12.TabIndex = 18
		Me.Label12.Text = "Determining breath pace:"
		Me.Label12.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label13
		'
		Me.Label13.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label13.Location = New System.Drawing.Point(181, 10)
		Me.Label13.Name = "Label13"
		Me.Label13.Size = New System.Drawing.Size(109, 20)
		Me.Label13.TabIndex = 19
		Me.Label13.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label14
		'
		Me.Label14.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label14.Location = New System.Drawing.Point(181, 30)
		Me.Label14.Name = "Label14"
		Me.Label14.Size = New System.Drawing.Size(109, 20)
		Me.Label14.TabIndex = 20
		Me.Label14.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label15
		'
		Me.Label15.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label15.Location = New System.Drawing.Point(181, 50)
		Me.Label15.Name = "Label15"
		Me.Label15.Size = New System.Drawing.Size(109, 20)
		Me.Label15.TabIndex = 21
		Me.Label15.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label16
		'
		Me.Label16.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label16.Location = New System.Drawing.Point(181, 70)
		Me.Label16.Name = "Label16"
		Me.Label16.Size = New System.Drawing.Size(109, 20)
		Me.Label16.TabIndex = 22
		Me.Label16.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label18
		'
		Me.Label18.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label18.Location = New System.Drawing.Point(181, 130)
		Me.Label18.Name = "Label18"
		Me.Label18.Size = New System.Drawing.Size(109, 20)
		Me.Label18.TabIndex = 24
		Me.Label18.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label19
		'
		Me.Label19.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label19.Location = New System.Drawing.Point(181, 170)
		Me.Label19.Name = "Label19"
		Me.Label19.Size = New System.Drawing.Size(109, 20)
		Me.Label19.TabIndex = 25
		Me.Label19.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label20
		'
		Me.Label20.Font = New System.Drawing.Font("Verdana", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label20.Location = New System.Drawing.Point(181, 210)
		Me.Label20.Name = "Label20"
		Me.Label20.Size = New System.Drawing.Size(109, 20)
		Me.Label20.TabIndex = 26
		Me.Label20.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label21
		'
		Me.Label21.BackColor = System.Drawing.Color.Transparent
		Me.Label21.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
		Me.Label21.ForeColor = System.Drawing.Color.White
		Me.Label21.Location = New System.Drawing.Point(184, 234)
		Me.Label21.Name = "Label21"
		Me.Label21.Size = New System.Drawing.Size(15, 15)
		Me.Label21.TabIndex = 27
		'
		'Label22
		'
		Me.Label22.BackColor = System.Drawing.Color.Transparent
		Me.Label22.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
		Me.Label22.ForeColor = System.Drawing.Color.White
		Me.Label22.Location = New System.Drawing.Point(204, 234)
		Me.Label22.Name = "Label22"
		Me.Label22.Size = New System.Drawing.Size(15, 15)
		Me.Label22.TabIndex = 28
		'
		'Label24
		'
		Me.Label24.BackColor = System.Drawing.Color.Transparent
		Me.Label24.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
		Me.Label24.ForeColor = System.Drawing.Color.White
		Me.Label24.Location = New System.Drawing.Point(244, 234)
		Me.Label24.Name = "Label24"
		Me.Label24.Size = New System.Drawing.Size(15, 15)
		Me.Label24.TabIndex = 30
		'
		'Label23
		'
		Me.Label23.BackColor = System.Drawing.Color.Transparent
		Me.Label23.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
		Me.Label23.ForeColor = System.Drawing.Color.White
		Me.Label23.Location = New System.Drawing.Point(224, 234)
		Me.Label23.Name = "Label23"
		Me.Label23.Size = New System.Drawing.Size(15, 15)
		Me.Label23.TabIndex = 29
		'
		'Label25
		'
		Me.Label25.BackColor = System.Drawing.Color.Transparent
		Me.Label25.Font = New System.Drawing.Font("Verdana", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label25.Location = New System.Drawing.Point(260, 231)
		Me.Label25.Name = "Label25"
		Me.Label25.Size = New System.Drawing.Size(33, 20)
		Me.Label25.TabIndex = 31
		Me.Label25.Text = "---"
		Me.Label25.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ProgressBar1
		'
		Me.ProgressBar1.Location = New System.Drawing.Point(184, 75)
		Me.ProgressBar1.MarqueeAnimationSpeed = 0
		Me.ProgressBar1.Name = "ProgressBar1"
		Me.ProgressBar1.Size = New System.Drawing.Size(106, 15)
		Me.ProgressBar1.TabIndex = 32
		Me.ProgressBar1.Visible = False
		'
		'ProgressBar3
		'
		Me.ProgressBar3.Location = New System.Drawing.Point(184, 115)
		Me.ProgressBar3.Name = "ProgressBar3"
		Me.ProgressBar3.Size = New System.Drawing.Size(106, 15)
		Me.ProgressBar3.TabIndex = 33
		'
		'Processing
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(304, 265)
		Me.Controls.Add(Me.DropInstruction)
		Me.Controls.Add(Me.Label25)
		Me.Controls.Add(Me.ProgressBar3)
		Me.Controls.Add(Me.ProgressBar1)
		Me.Controls.Add(Me.Label24)
		Me.Controls.Add(Me.Label23)
		Me.Controls.Add(Me.Label22)
		Me.Controls.Add(Me.Label21)
		Me.Controls.Add(Me.Label20)
		Me.Controls.Add(Me.Label19)
		Me.Controls.Add(Me.Label18)
		Me.Controls.Add(Me.Label16)
		Me.Controls.Add(Me.Label15)
		Me.Controls.Add(Me.Label14)
		Me.Controls.Add(Me.Label13)
		Me.Controls.Add(Me.Label12)
		Me.Controls.Add(Me.Label11)
		Me.Controls.Add(Me.Label10)
		Me.Controls.Add(Me.Label9)
		Me.Controls.Add(Me.ProgressBar5)
		Me.Controls.Add(Me.ProgressBar2)
		Me.Controls.Add(Me.Label8)
		Me.Controls.Add(Me.Label7)
		Me.Controls.Add(Me.Label6)
		Me.Controls.Add(Me.Label5)
		Me.Controls.Add(Me.Label4)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.ProgressBar4)
		Me.Controls.Add(Me.Label1)
		Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog
		Me.MaximizeBox = False
		Me.MaximumSize = New System.Drawing.Size(310, 290)
		Me.MinimizeBox = False
		Me.MinimumSize = New System.Drawing.Size(310, 290)
		Me.Name = "Processing"
		Me.SizeGripStyle = System.Windows.Forms.SizeGripStyle.Hide
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		Me.Text = "  Fisher Behavior  |  Heart Rate Visualizer"
		Me.ResumeLayout(False)

	End Sub
    Friend WithEvents DropInstruction As System.Windows.Forms.Label
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents ProgressBar4 As System.Windows.Forms.ProgressBar
    Friend WithEvents Label2 As System.Windows.Forms.Label
    Friend WithEvents Label3 As System.Windows.Forms.Label
    Friend WithEvents Label4 As System.Windows.Forms.Label
    Friend WithEvents Label5 As System.Windows.Forms.Label
    Friend WithEvents Label6 As System.Windows.Forms.Label
    Friend WithEvents Label7 As System.Windows.Forms.Label
    Friend WithEvents Label8 As System.Windows.Forms.Label
    Friend WithEvents ProgressBar2 As System.Windows.Forms.ProgressBar
    Friend WithEvents Label9 As System.Windows.Forms.Label
    Friend WithEvents ProgressBar5 As System.Windows.Forms.ProgressBar
    Friend WithEvents Label10 As System.Windows.Forms.Label
    Friend WithEvents Label11 As System.Windows.Forms.Label
    Friend WithEvents Label12 As System.Windows.Forms.Label
    Friend WithEvents Label13 As System.Windows.Forms.Label
    Friend WithEvents Label14 As System.Windows.Forms.Label
    Friend WithEvents Label15 As System.Windows.Forms.Label
    Friend WithEvents Label16 As System.Windows.Forms.Label
    Friend WithEvents Label18 As System.Windows.Forms.Label
    Friend WithEvents Label19 As System.Windows.Forms.Label
    Friend WithEvents Label20 As System.Windows.Forms.Label
    Friend WithEvents Label21 As System.Windows.Forms.Label
    Friend WithEvents Label22 As System.Windows.Forms.Label
    Friend WithEvents Label24 As System.Windows.Forms.Label
    Friend WithEvents Label23 As System.Windows.Forms.Label
    Friend WithEvents Label25 As System.Windows.Forms.Label
    Friend WithEvents ProgressBar1 As System.Windows.Forms.ProgressBar
    Friend WithEvents ProgressBar3 As System.Windows.Forms.ProgressBar
End Class
