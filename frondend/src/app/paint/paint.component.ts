import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { fromEvent } from 'rxjs/observable/fromEvent'
import { mergeMap, takeUntil, switchMap } from 'rxjs/operators'

import { PaintService } from './paint.service'
import { PaintApiService } from './paint.api.service'

@Component({
  selector: 'app-paint',
  templateUrl: './paint.component.html',
  styleUrls: ['./paint.component.scss']
})
export class PaintComponent implements OnInit, AfterViewInit {

  generatedImage:string = "https://cdn.cnn.com/cnnnext/dam/assets/201226140818-01-trump-south-lawn-1212-large-tease.jpg" 
  constructor(private paintSvc: PaintService, 
              private elRef: ElementRef,
              private paintApi : PaintApiService) { }

  ngOnInit() {
    console.log(this.elRef)
    this.paintSvc.initialize(this.elRef.nativeElement)
    this.startPainting()
  }

  ngAfterViewInit() {
  }

  isMobile(){
    // credit to Timothy Huang for this regex test: 
    // https://dev.to/timhuang/a-simple-way-to-detect-if-browser-is-on-a-mobile-device-with-javascript-44j3
    if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){
        return true
    }
    else{
          return false
    }
  } 
  transform()
  {
    const { nativeElement } = this.elRef;
    const canvas = nativeElement.querySelector('canvas') as HTMLCanvasElement
    console.log(canvas.toDataURL())
    //console.log(this.paintSvc.getImageData(canvas))
    this.generatedImage = canvas.toDataURL()
    
    
    this.paintApi.generate_shoe(canvas.toDataURL()).subscribe(res => {
        //let item = JSON.parse(res);
        //test_too_large
        this.generatedImage =  res
       
      },
      console.error
    );
   
    //var imageData = this.paintSvc.getImageData(canvas)
    //var decoder = new TextDecoder('utf8');
    //var b64encoded = btoa(decoder.decode(imageData.data));
    //console.log(b64encoded)
  }
  reset()
  {
    const { nativeElement } = this.elRef;
    const canvas = nativeElement.querySelector('canvas') as HTMLCanvasElement
    this.paintSvc.clear(canvas)
  }

  private startPainting() {
    const { nativeElement } = this.elRef;
    const canvas = nativeElement.querySelector('canvas') as HTMLCanvasElement
    const move$ = fromEvent<MouseEvent>(canvas, 'mousemove')
    const down$ = fromEvent<MouseEvent>(canvas, 'mousedown')
    const up$ = fromEvent<MouseEvent>(canvas, 'mouseup')
    const paints$ = down$.pipe(
      mergeMap(down => move$.pipe(takeUntil(up$)))
      // mergeMap(down => move$)
    );

    down$.subscribe(console.info)

    const offset = getOffset(canvas)

    paints$.subscribe((event) => {
      const clientX = event.clientX - offset.left
      const clientY = event.clientY - offset.top
      this.paintSvc.paint({ clientX, clientY })
    });
  }

}


function getOffset(el: HTMLElement) {
  const rect = el.getBoundingClientRect();

  return {
    top: rect.top + document.body.scrollTop,
    left: rect.left + document.body.scrollLeft
  }
}