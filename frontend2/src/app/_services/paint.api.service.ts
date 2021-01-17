import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, of} from 'rxjs';
import 'rxjs/add/operator/catch';
import {API_URL} from '../../environments/environment';
import { catchError, retry } from 'rxjs/operators';

@Injectable()
export class PaintApiService {
    constructor(private http: HttpClient) {}

    generate_shoe(image: string): Observable<string> {
        return this.http.get<any>(`${API_URL}/generate_shoe?image=${image}`)
          .pipe(
            catchError(err => {
              console.log(err);
              return of(null);
                })
          );
    }
    generate_edge(image:string) : Observable<string> {
      return this.http.get<any>(`${API_URL}/generate_edge?image=${image}`)
        .pipe(
          catchError(err => {
            console.log(err);
            return of(null);
              })
        );
  }
    //test_too_large
    test_too_large(image: string): Observable<string> {
      return this.http.get<any>(`${API_URL}/test_too_large`)
        .pipe(
          catchError(err => {
            console.log(err);
            return of(null);
              })
        );
  }
    //Put new Patient
    generate_shoe2(image : any): Observable<string> {
      const formData = new FormData();
      //formData.append('image',  JSON.stringify(image));
      formData.append('image',  JSON.stringify(image));
      //urlSearchParams.append('password', password);
      return this.http.post<any>(`${API_URL}/generate_shoe`, formData)
        .pipe(
          catchError(err => {
            console.log(err);
            return of(null);
              })
        );
  }

}