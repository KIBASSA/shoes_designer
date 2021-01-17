import { Component, OnInit } from '@angular/core';
import { PaintApiService } from '../_services/paint.api.service'
@Component({
  selector: 'app-twophases',
  templateUrl: './twophases.component.html',
  styleUrls: ['./twophases.component.css']
})
export class TwophasesComponent implements OnInit {
  public imagePath;
  imgURL: any;
  imgEdgeURL : any;
  imgIBlackLeather: any;
  public message: string;

  constructor(private paintApi : PaintApiService) {}

  ngOnInit(): void {}
  fileChange(files:any) {
      if (files.length === 0)
        return;
  
      var mimeType = files[0].type;
      if (mimeType.match(/image\/*/) == null) {
        this.message = "Only images are supported.";
        return;
      }
  
      var reader = new FileReader();
      this.imagePath = files;
      reader.readAsDataURL(files[0]); 
      reader.onload = (_event) => { 
        this.imgURL = reader.result;
        console.log(this.imgURL)
      }
   }

   convertImageToEdge()
   {
     this.paintApi.generate_edge(this.imgURL).subscribe(res=> 
      {
        this.imgEdgeURL = res
      })
   }

   convertEdgeToImage()
   {
    this.paintApi.generate_shoe_by_hed(this.imgEdgeURL).subscribe(res=> 
      {
        this.imgIBlackLeather = res
      })
   }
}
