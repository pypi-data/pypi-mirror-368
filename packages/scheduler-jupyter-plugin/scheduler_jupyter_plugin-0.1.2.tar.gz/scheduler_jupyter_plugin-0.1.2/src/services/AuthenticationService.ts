/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { requestAPI } from '../handler/Handler';
import { IAuthCredentials } from '../login/LoginInterfaces';
import { LOGIN_STATE, STATUS_SUCCESS } from '../utils/Const';

export class AuthenticationService {
  static readonly loginAPI = async (
    setLoginState: (value: boolean) => void,
    setLoginError: (value: boolean) => void
  ) => {
    const data = await requestAPI('login', {
      method: 'POST'
    });
    if (typeof data === 'object' && data !== null) {
      const loginStatus = (data as { login: string }).login;
      if (loginStatus === STATUS_SUCCESS) {
        setLoginState(true);
        setLoginError(false);
        localStorage.setItem('loginState', LOGIN_STATE);
      } else {
        setLoginState(false);
        localStorage.removeItem('loginState');
      }
    }
  };

  /**
   * Authentication
   * @param checkApiEnabled
   * @returns credentials
   */

  static readonly authCredentialsAPI = async (
    checkApiEnabled: boolean = true
  ): Promise<IAuthCredentials | undefined> => {
    try {
      const data = await requestAPI('credentials');
      if (typeof data === 'object' && data !== null) {
        const credentials: IAuthCredentials = {
          access_token: (data as { access_token: string }).access_token,
          project_id: (data as { project_id: string }).project_id,
          region_id: (data as { region_id: string }).region_id,
          config_error: (data as { config_error: number }).config_error,
          login_error: (data as { login_error: number }).login_error
        };
        return credentials;
      }
    } catch (reason) {
      console.error(`Error on GET credentials.\n${reason}`);
    }
  };
}
